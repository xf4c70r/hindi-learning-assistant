import os
import sys
from datetime import datetime

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

import django
django.setup()

from api.services.mongo_service import mongo_service
from qa_engine.qa_model import qa_model
from youtube_transcript_api import YouTubeTranscriptApi

def get_unprocessed_videos():
    """Get videos that haven't been processed yet"""
    return list(mongo_service.db.youtube_videos.find({
        'processed': {'$ne': True}
    }))

def save_transcript(video_id, transcript_data):
    """Save transcript to MongoDB"""
    doc = {
        'video_id': video_id,
        'transcript': transcript_data,
        'created_at': datetime.utcnow()
    }
    return mongo_service.db.transcripts.insert_one(doc)

def save_qa_pairs(transcript_id, qa_pairs, video_id):
    """Save QA pairs to MongoDB"""
    qa_docs = []
    for qa in qa_pairs:
        qa_doc = {
            'transcript_id': transcript_id,
            'video_id': video_id,
            'question': qa['question'],
            'answer': qa['answer'],
            'type': qa.get('type', 'novice'),
            'options': qa.get('options', None),
            'created_at': datetime.utcnow()
        }
        qa_docs.append(qa_doc)
    
    if qa_docs:
        return mongo_service.db.qa_pairs.insert_many(qa_docs)
    return None

def process_video(video):
    """Process a single video: get transcript, generate QA pairs"""
    video_id = video['video_id']
    print(f"\n🎥 Processing video: {video['title']} ({video_id})")
    
    try:
        # Get transcript
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['hi'])
        transcript_text = ' '.join(item['text'] for item in transcript_list)
        
        # Save transcript
        transcript_result = save_transcript(video_id, transcript_text)
        print("✅ Saved transcript")
        
        # Generate and save QA pairs for different types
        for qa_type in ['novice', 'mcq', 'fill_blanks']:
            print(f"📝 Generating {qa_type} questions...")
            qa_pairs = qa_model.generate_questions(transcript_text, qa_type)
            
            if isinstance(qa_pairs, dict) and 'qa_pairs' in qa_pairs:
                qa_pairs = qa_pairs['qa_pairs']
            
            save_qa_pairs(transcript_result.inserted_id, qa_pairs, video_id)
            print(f"✅ Saved {len(qa_pairs)} {qa_type} questions")
        
        # Mark video as processed
        mongo_service.db.youtube_videos.update_one(
            {'_id': video['_id']},
            {
                '$set': {
                    'processed': True,
                    'processed_at': datetime.utcnow()
                }
            }
        )
        
        return True
        
    except Exception as e:
        print(f"❌ Error processing video {video_id}: {str(e)}")
        # Mark video as failed
        mongo_service.db.youtube_videos.update_one(
            {'_id': video['_id']},
            {
                '$set': {
                    'processed': False,
                    'error': str(e),
                    'last_attempt': datetime.utcnow()
                }
            }
        )
        return False

def main():
    print("🚀 Starting dataset generation...")
    
    # Create indexes if they don't exist
    mongo_service.db.transcripts.create_index('video_id', unique=True)
    mongo_service.db.qa_pairs.create_index([('transcript_id', 1), ('type', 1)])
    
    # Get unprocessed videos
    videos = get_unprocessed_videos()
    print(f"📋 Found {len(videos)} unprocessed videos")
    
    successful = 0
    failed = 0
    
    for video in videos:
        if process_video(video):
            successful += 1
        else:
            failed += 1
    
    print("\n=== Generation Summary ===")
    print(f"✅ Successfully processed: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total QA pairs: {mongo_service.db.qa_pairs.count_documents({})}")

if __name__ == "__main__":
    main() 