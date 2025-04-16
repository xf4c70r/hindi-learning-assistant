from youtube_transcript_api import YouTubeTranscriptApi
import re

def extract_video_id(url):
    """Extract video ID from YouTube URL."""
    # Regular expressions for different YouTube URL formats
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',  # Standard and short URLs
        r'(?:embed\/)([0-9A-Za-z_-]{11})',   # Embed URLs
        r'^([0-9A-Za-z_-]{11})$'             # Direct video ID
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def get_transcript(video_id):
    """Get transcript from YouTube video."""
    try:
        # Try to get Hindi transcript first
        print(f"Attempting to fetch transcripts for video ID: {video_id}")
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        print("Available languages:", [t.language_code for t in transcript_list])
        
        # Try to get Hindi transcript
        try:
            transcript = transcript_list.find_transcript(['hi'])
            language = 'hi'
            print("Found Hindi transcript")
        except Exception as e:
            print(f"Hindi transcript not found: {str(e)}")
            # If Hindi not available, get any available transcript
            transcript = transcript_list.find_transcript(['en'])
            language = 'en'
            print("Found English transcript")
        
        transcript_data = transcript.fetch()
        print(f"Successfully fetched {language} transcript with {len(transcript_data)} entries")
        return transcript_data, language
    except Exception as e:
        print(f"Error in get_transcript: {str(e)}")
        import traceback
        print(traceback.format_exc())
        raise ValueError(f"Could not fetch transcript: {str(e)}")

def format_transcript(transcript_data):
    """Format transcript data into readable text."""
    try:
        formatted_text = ' '.join([entry['text'] for entry in transcript_data])
        print(f"Formatted transcript length: {len(formatted_text)} characters")
        return formatted_text
    except Exception as e:
        print(f"Error formatting transcript: {str(e)}")
        raise 