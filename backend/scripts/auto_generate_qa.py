import os
from datetime import datetime
import logging
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
import yt_dlp
from pymongo import MongoClient
import certifi
from qa_engine.qa_model import qa_model

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
PLAYLIST_URL = "https://www.youtube.com/playlist?list=PL48CaRIHVwhX-QW3yVgbbKUhZYPKpv0wY"
QUESTION_TYPES = ["novice", "mcq"]
LANGUAGE_PREFERENCES = ['hi', 'hi-IN', 'en', 'en-IN', 'en-US']

class MongoConnection:
    def __init__(self):
        self.client = None
        self.db = None
        self.connect()

    def connect(self):
        """Connect to MongoDB Atlas"""
        try:
            uri = os.getenv('MONGODB_URI')
            if not uri:
                raise ValueError("MONGODB_URI environment variable is not set")
            
            self.client = MongoClient(uri, tlsCAFile=certifi.where())
            self.db = self.client[os.getenv('MONGODB_NAME', 'hindi_qa_db')]
            logger.info("Connected to MongoDB Atlas")
        except Exception as e:
            logger.error(f"Error connecting to MongoDB: {str(e)}")
            raise

    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()

def get_new_videos(db) -> List[Dict[str, Any]]:
    """Fetch new videos from the YouTube playlist"""
    try:
        ydl_opts = {
            'quiet': True,
            'extract_flat': True,
            'dump_single_json': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(PLAYLIST_URL, download=False)
            videos = [
                {
                    'url': entry['url'],
                    'video_id': entry['id'],
                    'title': entry.get('title', ''),
                    'duration': entry.get('duration', 0),
                    'fetched_at': datetime.utcnow()
                }
                for entry in info['entries']
            ]

        # Filter out videos that are already processed
        existing_ids = set(doc['video_id'] for doc in db.youtube_videos.find({}, {'video_id': 1}))
        new_videos = [video for video in videos if video['video_id'] not in existing_ids]
        
        return new_videos

    except Exception as e:
        logger.error(f"Error fetching videos: {str(e)}")
        return []

def get_available_transcripts(video_id: str) -> List[Dict[str, Any]]:
    """Get list of available transcripts for a video"""
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        return transcript_list
    except Exception as e:
        logger.error(f"Error listing transcripts for video {video_id}: {str(e)}")
        return None

def get_transcript(video_id: str) -> Optional[str]:
    """Get transcript for a video with language fallbacks"""
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # Try manual transcripts first
        for lang in LANGUAGE_PREFERENCES:
            try:
                transcript = transcript_list.find_manually_created_transcript([lang])
                return ' '.join(item['text'] for item in transcript.fetch())
            except:
                continue

        # Try auto-generated transcripts
        for lang in LANGUAGE_PREFERENCES:
            try:
                transcript = transcript_list.find_generated_transcript([lang])
                return ' '.join(item['text'] for item in transcript.fetch())
            except:
                continue

        # If no preferred language found, try any available transcript
        try:
            transcript = transcript_list.find_transcript([])
            return ' '.join(item['text'] for item in transcript.fetch())
        except:
            pass

        logger.warning(f"No suitable transcript found for video {video_id}")
        return None

    except Exception as e:
        logger.error(f"Error getting transcript for video {video_id}: {str(e)}")
        return None

def generate_qa_pairs(text: str, video_id: str) -> List[Dict[str, Any]]:
    """Generate QA pairs from text"""
    qa_pairs = []
    try:
        for q_type in QUESTION_TYPES:
            pairs = qa_model.generate_questions(text, q_type)
            if isinstance(pairs, list):
                for pair in pairs:
                    pair['video_id'] = video_id
                    pair['type'] = q_type
                    pair['created_at'] = datetime.utcnow()
                    qa_pairs.append(pair)
    except Exception as e:
        logger.error(f"Error generating QA pairs: {str(e)}")
    
    return qa_pairs

def process_video(db, video: Dict[str, Any]) -> bool:
    """Process a single video"""
    try:
        video_id = video['video_id']
        logger.info(f"Processing video: {video['title']} ({video_id})")

        # Check available transcripts
        transcript_list = get_available_transcripts(video_id)
        if not transcript_list:
            logger.warning(f"No transcripts available for video {video_id}")
            # Save video as processed but without transcript
            video['processed'] = True
            video['has_transcript'] = False
            db.youtube_videos.insert_one(video)
            return False

        # Get transcript
        transcript = get_transcript(video_id)
        if not transcript:
            logger.error(f"Could not get transcript for video {video_id}")
            # Save video as processed but without transcript
            video['processed'] = True
            video['has_transcript'] = False
            db.youtube_videos.insert_one(video)
            return False

        # Save transcript
        transcript_doc = {
            'video_id': video_id,
            'title': video['title'],
            'content': transcript,
            'language': 'hi',  # Default to Hindi even if we got another language
            'created_at': datetime.utcnow()
        }
        result = db.transcripts.insert_one(transcript_doc)
        transcript_id = result.inserted_id

        # Generate and save QA pairs
        qa_pairs = generate_qa_pairs(transcript, video_id)
        if qa_pairs:
            for pair in qa_pairs:
                pair['transcript_id'] = transcript_id
            db.qa_pairs.insert_many(qa_pairs)

        # Mark video as processed
        video['processed'] = True
        video['has_transcript'] = True
        db.youtube_videos.insert_one(video)

        logger.info(f"Successfully processed video {video_id} with {len(qa_pairs)} QA pairs")
        return True

    except Exception as e:
        logger.error(f"Error processing video {video.get('video_id')}: {str(e)}")
        return False

def main():
    """Main function to run the automation"""
    logger.info("Starting automated QA generation process")
    mongo = None
    
    try:
        # Connect to MongoDB
        mongo = MongoConnection()
        
        # Get new videos
        new_videos = get_new_videos(mongo.db)
        if not new_videos:
            logger.info("No new videos to process")
            return

        logger.info(f"Found {len(new_videos)} new videos to process")

        # Process each video
        success_count = 0
        for video in new_videos:
            if process_video(mongo.db, video):
                success_count += 1

        logger.info(f"Completed processing. Successfully processed {success_count}/{len(new_videos)} videos")

    except Exception as e:
        logger.error(f"Error in main process: {str(e)}")
    finally:
        if mongo:
            mongo.close()

if __name__ == "__main__":
    main() 