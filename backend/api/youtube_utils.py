from youtube_transcript_api import YouTubeTranscriptApi
import re
import logging
import time
from random import uniform

logger = logging.getLogger(__name__)

def extract_video_id(url):
    """Extract video ID from YouTube URL."""
    logger.info(f"Attempting to extract video ID from URL: {url}")
    
    # Regular expressions for different YouTube URL formats
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',  # Standard and short URLs
        r'(?:embed\/)([0-9A-Za-z_-]{11})',   # Embed URLs
        r'^([0-9A-Za-z_-]{11})$'             # Direct video ID
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            video_id = match.group(1)
            logger.info(f"Successfully extracted video ID: {video_id}")
            return video_id
    
    logger.error(f"Failed to extract video ID from URL: {url}")
    return None

def check_video_captions(video_id):
    """Check if a video has captions available."""
    try:
        logger.info(f"Checking captions availability for video ID: {video_id}")
        api = YouTubeTranscriptApi()
        transcript_list = api.list(video_id)
        available_languages = [t.language_code for t in transcript_list]
        logger.info(f"Available caption languages: {available_languages}")
        return available_languages
    except Exception as e:
        logger.error(f"Error checking captions for video {video_id}: {str(e)}")
        return []

def get_transcript_with_retry(video_id, max_retries=3, initial_delay=1):
    """Get transcript with retry logic."""
    delay = initial_delay
    last_exception = None
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Attempting to fetch transcripts for video ID: {video_id}")
            api = YouTubeTranscriptApi()
            transcript_list = api.list(video_id)
            available_languages = [t.language_code for t in transcript_list]
            logger.info(f"Available languages: {available_languages}")
            
            # Try to get Hindi transcript
            try:
                transcript = transcript_list.find_transcript(['hi'])
                language = 'hi'
                logger.info("Found Hindi transcript")
            except Exception as e:
                logger.warning(f"Hindi transcript not found: {str(e)}")
                # If Hindi not available, get any available transcript
                try:
                    transcript = transcript_list.find_transcript(['en'])
                    language = 'en'
                    logger.info("Found English transcript")
                except Exception as e2:
                    logger.warning(f"English transcript not found: {str(e2)}")
                    # Try to get any available transcript
                    if available_languages:
                        first_language = available_languages[0]
                        transcript = transcript_list.find_transcript([first_language])
                        language = first_language
                        logger.info(f"Found {first_language} transcript")
                    else:
                        raise ValueError("No transcripts available for this video")
            
            # Add more detailed logging before fetching
            logger.info(f"About to fetch transcript for language: {language}")
            
            # Try multiple approaches to fetch the transcript
            transcript_data = None
            
            # Approach 1: Standard fetch
            try:
                transcript_data = transcript.fetch()
                logger.info("Successfully fetched transcript using standard method")
            except Exception as e:
                logger.warning(f"Standard fetch failed: {str(e)}")
                
                # Approach 2: Try with different parameters
                try:
                    transcript_data = transcript.fetch(preserve_formatting=True)
                    logger.info("Successfully fetched transcript with preserve_formatting=True")
                except Exception as e2:
                    logger.warning(f"Preserve formatting fetch failed: {str(e2)}")
                    
                    # Approach 3: Try getting raw data
                    try:
                        # Try to access the raw transcript data
                        if hasattr(transcript, '_transcript_data'):
                            transcript_data = transcript._transcript_data
                            logger.info("Successfully got raw transcript data")
                        else:
                            raise ValueError("No raw transcript data available")
                    except Exception as e3:
                        logger.error(f"All fetch methods failed: {str(e3)}")
                        raise
            
            # Validate the transcript data
            if not transcript_data:
                raise ValueError("Received empty transcript data from YouTube")
            
            logger.info(f"Successfully fetched {language} transcript with {len(transcript_data)} entries")
            logger.debug(f"First entry preview: {transcript_data[0] if transcript_data else 'No data'}")
            
            return transcript_data, language
            
        except Exception as e:
            last_exception = e
            error_msg = str(e)
            logger.error(f"Attempt {attempt + 1}/{max_retries} failed: {error_msg}")
            
            # Check for specific error types
            if "YouTube is blocking requests from your IP" in error_msg:
                logger.error("🚫 IP BLOCKED: YouTube has blocked your IP address!")
                logger.error("This usually happens due to:")
                logger.error("1. Too many requests in a short time")
                logger.error("2. Using a cloud provider IP (AWS, GCP, Azure)")
                logger.error("3. Automated requests detected")
                logger.error("Solutions:")
                logger.error("- Wait 15-30 minutes and try again")
                logger.error("- Use a different network/VPN")
                logger.error("- Implement better rate limiting")
                
                # Don't retry for IP blocking - it won't help
                raise ValueError("YouTube has blocked your IP address. Please wait 15-30 minutes and try again, or use a different network.")
                
            elif "no element found" in error_msg.lower():
                logger.error("YouTube returned malformed/empty XML response. This usually means:")
                logger.error("1. The video doesn't have proper captions")
                logger.error("2. YouTube's API is having issues")
                logger.error("3. The video might be private or restricted")
                logger.error("4. Auto-generated captions might have parsing issues")
                
                # For this specific error, try a different approach
                if attempt == 0:  # Only try alternative approach on first attempt
                    logger.info("Trying alternative approach with direct API call...")
                    try:
                        # Try using the direct API method
                        api = YouTubeTranscriptApi()
                        transcript_data = api.fetch(video_id, languages=['hi', 'en'])
                        logger.info("Successfully fetched transcript using direct API method")
                        return transcript_data, 'hi' if any('hi' in str(t) for t in transcript_data) else 'en'
                    except Exception as alt_e:
                        logger.error(f"Alternative approach also failed: {str(alt_e)}")
                
                # Don't retry for this type of error after trying alternative
                raise ValueError(f"Could not fetch transcript: {error_msg}")
            elif "Too Many Requests" in error_msg:
                wait_time = delay * (1 + uniform(0, 0.1))  # Add some randomness
                logger.warning(f"Rate limited by YouTube. Waiting {wait_time:.2f} seconds before retry {attempt + 1}/{max_retries}")
                time.sleep(wait_time)
                delay *= 2  # Exponential backoff
            else:
                # For other errors, don't retry
                logger.error(f"Non-retryable error: {error_msg}")
                raise
    
    # If we've exhausted all retries
    raise ValueError(f"Could not fetch transcript after {max_retries} attempts: {str(last_exception)}")

def get_transcript(video_id):
    """Get transcript from YouTube video."""
    try:
        logger.info(f"Attempting to fetch transcripts for video ID: {video_id}")
        
        # Add a small delay to be respectful of YouTube's rate limits
        time.sleep(1)
        
        return get_transcript_with_retry(video_id)
    except Exception as e:
        logger.error(f"Error in get_transcript: {str(e)}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise ValueError(f"Could not fetch transcript: {str(e)}")

def format_transcript(transcript_data):
    """Format transcript data into readable text."""
    try:
        logger.info(f"Formatting transcript with {len(transcript_data)} entries")
        
        # Clean and join the text entries
        formatted_lines = []
        for entry in transcript_data:
            # Handle both old dictionary format and new FetchedTranscriptSnippet format
            if hasattr(entry, 'text'):
                # New API format: FetchedTranscriptSnippet object
                text = entry.text.strip()
            elif isinstance(entry, dict) and 'text' in entry:
                # Old API format: dictionary
                text = entry['text'].strip()
            else:
                logger.warning(f"Unknown entry format: {type(entry)}")
                continue
            
            # Skip empty lines
            if not text:
                continue
                
            # Skip music notations and other non-text content
            skip_patterns = ['[संगीत]', '[Music]', '[Applause]', '[Laughter]', '[Background]']
            if any(pattern in text for pattern in skip_patterns):
                continue
            
            # Clean up common formatting issues
            text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
            text = text.replace(' ।', '।')  # Fix spacing around punctuation
            text = text.replace(' ?', '?')
            text = text.replace(' !', '!')
            text = text.replace('..', '…')  # Convert multiple dots to ellipsis
            
            # Only add non-empty lines after cleaning
            if text.strip():
                formatted_lines.append(text)
        
        # Join lines with proper spacing
        formatted_text = ' '.join(formatted_lines)
        
        # Final cleanup
        formatted_text = formatted_text.strip()
        formatted_text = re.sub(r'\s+', ' ', formatted_text)  # Final whitespace normalization
        
        # Logging
        logger.info(f"Formatted transcript length: {len(formatted_text)} characters")
        logger.debug(f"Formatted transcript preview: {formatted_text[:200]}")
        
        return formatted_text
        
    except Exception as e:
        logger.error(f"Error formatting transcript: {str(e)}")
        logger.error(f"Transcript data preview: {str(transcript_data[:2])}")
        raise ValueError(f"Failed to format transcript: {str(e)}") 