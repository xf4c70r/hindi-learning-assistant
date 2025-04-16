from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
import re

def extract_video_id(url):
    """Extract video ID from YouTube URL."""
    if not url:
        raise ValueError("URL cannot be empty")

    # Regular expressions for different YouTube URL formats
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',  # Standard and short URLs
        r'(?:embed\/)([0-9A-Za-z_-]{11})',   # Embed URLs
        r'(?:youtu\.be\/)([0-9A-Za-z_-]{11})',  # Shortened URLs
        r'^([0-9A-Za-z_-]{11})$'             # Direct video ID
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            video_id = match.group(1)
            if len(video_id) == 11:  # YouTube video IDs are always 11 characters
                return video_id
    raise ValueError("Could not extract valid YouTube video ID from URL")

def get_transcript(video_id):
    """Get transcript from YouTube video."""
    if not video_id or len(video_id) != 11:
        raise ValueError("Invalid YouTube video ID")

    try:
        print(f"Attempting to fetch transcripts for video ID: {video_id}")
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        available_languages = [t.language_code for t in transcript_list]
        print("Available languages:", available_languages)
        
        # Try to get transcript in preferred languages
        preferred_languages = ['hi', 'en', 'en-IN']  # Priority order
        transcript = None
        language = None
        
        for lang in preferred_languages:
            try:
                if lang in available_languages:
                    transcript = transcript_list.find_transcript([lang])
                    language = lang
                    print(f"Found {lang} transcript")
                    break
            except Exception as e:
                print(f"Could not fetch {lang} transcript: {str(e)}")
                continue
        
        if not transcript and available_languages:
            # If none of our preferred languages are available, use the first available
            first_lang = available_languages[0]
            transcript = transcript_list.find_transcript([first_lang])
            language = first_lang
            print(f"Using available transcript in {first_lang}")
        
        if not transcript:
            raise NoTranscriptFound(video_id)
        
        transcript_data = transcript.fetch()
        print(f"Successfully fetched {language} transcript with {len(transcript_data)} entries")
        
        # Validate transcript data
        if not transcript_data or not isinstance(transcript_data, list):
            raise ValueError("Invalid transcript data format")
        
        return transcript_data, language

    except TranscriptsDisabled:
        raise ValueError("Transcripts are disabled for this video")
    except VideoUnavailable:
        raise ValueError("The video is unavailable or private")
    except NoTranscriptFound:
        raise ValueError("No transcripts found for this video")
    except Exception as e:
        print(f"Error in get_transcript: {str(e)}")
        import traceback
        print(traceback.format_exc())
        raise ValueError(f"Could not fetch transcript: {str(e)}")

def format_transcript(transcript_data):
    """Format transcript data into readable text."""
    try:
        if not transcript_data or not isinstance(transcript_data, list):
            raise ValueError("Invalid transcript data format")

        formatted_text = ' '.join(
            entry.get('text', '').strip()
            for entry in transcript_data
            if entry.get('text')
        )

        if not formatted_text:
            raise ValueError("No valid text found in transcript")

        print(f"Formatted transcript length: {len(formatted_text)} characters")
        return formatted_text
    except Exception as e:
        print(f"Error formatting transcript: {str(e)}")
        raise ValueError(f"Failed to format transcript: {str(e)}") 