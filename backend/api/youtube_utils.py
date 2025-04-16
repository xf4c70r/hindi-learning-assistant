from youtube_transcript_api import YouTubeTranscriptApi
import re
import logging

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

def get_transcript(video_id):
    """Get transcript from YouTube video."""
    try:
        logger.info(f"Attempting to fetch transcripts for video ID: {video_id}")
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
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
            transcript = transcript_list.find_transcript(['en'])
            language = 'en'
            logger.info("Found English transcript")
        
        transcript_data = transcript.fetch()
        logger.info(f"Successfully fetched {language} transcript with {len(transcript_data)} entries")
        return transcript_data, language
    except Exception as e:
        logger.error(f"Error in get_transcript: {str(e)}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise ValueError(f"Could not fetch transcript: {str(e)}")

def format_transcript(transcript_data):
    """Format transcript data into readable text."""
    try:
        logger.info(f"Formatting transcript with {len(transcript_data)} entries")
        formatted_text = ' '.join([entry['text'] for entry in transcript_data])
        logger.info(f"Formatted transcript length: {len(formatted_text)} characters")
        return formatted_text
    except Exception as e:
        logger.error(f"Error formatting transcript: {str(e)}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise 