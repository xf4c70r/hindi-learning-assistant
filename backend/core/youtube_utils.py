from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs

def get_video_id(url):
    """
    Extract video ID from YouTube URL
    """
    parsed_url = urlparse(url)
    if parsed_url.hostname == 'youtu.be':
        return parsed_url.path[1:]
    if parsed_url.hostname in ('www.youtube.com', 'youtube.com'):
        if parsed_url.path == '/watch':
            return parse_qs(parsed_url.query)['v'][0]
    return None

def get_transcript(youtube_url, preferred_languages=['hi', 'en']):
    """
    Get transcript from YouTube video, trying multiple languages
    """
    try:
        video_id = get_video_id(youtube_url)
        if not video_id:
            raise ValueError("Invalid YouTube URL")

        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # Try each language in order of preference
        for lang in preferred_languages:
            try:
                transcript = transcript_list.find_transcript([lang])
                return transcript.fetch(), lang
            except:
                continue
                
        # If no preferred language found, try to get any available transcript
        try:
            transcript = transcript_list.find_transcript(['en'])  # Default to English
            return transcript.fetch(), 'en'
        except:
            # Try to get any manual transcript
            manual_transcripts = [t for t in transcript_list if not t.is_generated]
            if manual_transcripts:
                transcript = manual_transcripts[0]
                return transcript.fetch(), transcript.language_code
            
            # Last resort: get any available transcript
            transcript = next(iter(transcript_list))
            return transcript.fetch(), transcript.language_code

    except Exception as e:
        raise ValueError(f"Error fetching transcript: {str(e)}")

def format_transcript(transcript_data):
    """
    Format transcript data into readable text
    Each transcript entry has 'text', 'start', 'duration' attributes
    """
    formatted_entries = []
    for entry in transcript_data:
        # Each entry is a TranscriptSnippet object with text attribute
        formatted_entries.append(entry.text)
    return " ".join(formatted_entries) 