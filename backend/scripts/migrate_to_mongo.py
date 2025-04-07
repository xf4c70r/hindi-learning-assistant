import os
import sys
import django
from datetime import datetime

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.contrib.auth.models import User
from api.models import Transcript, Question
from api.services.mongo_service import mongo_service

def migrate_transcript(transcript):
    """Migrate a single transcript and its questions to MongoDB"""
    try:
        # Convert Django model to MongoDB document
        transcript_doc = {
            'django_id': transcript.id,  # Keep reference to Django ID
            'user_id': transcript.user.id,
            'video_id': transcript.video_id,
            'title': transcript.title,
            'content': transcript.content,
            'language': transcript.language,
            'is_favorite': transcript.is_favorite,
            'created_at': transcript.created_at,
            'updated_at': transcript.updated_at
        }
        
        # Insert transcript
        result = mongo_service.db.transcripts.insert_one(transcript_doc)
        mongo_transcript_id = result.inserted_id
        print(f"✅ Migrated transcript: {transcript.title}")
        
        # Migrate associated questions
        for question in transcript.questions.all():
            question_doc = {
                'django_id': question.id,
                'transcript_id': mongo_transcript_id,  # Reference to MongoDB transcript
                'django_transcript_id': transcript.id,  # Keep reference to Django transcript
                'question_type': question.question_type,
                'question_text': question.question_text,
                'answer': question.answer,
                'options': question.options,
                'is_favorite': question.is_favorite,
                'attempts': question.attempts,
                'correct_attempts': question.correct_attempts,
                'created_at': question.created_at
            }
            mongo_service.db.questions.insert_one(question_doc)
        
        print(f"✅ Migrated {transcript.questions.count()} questions for transcript: {transcript.title}")
        return True
        
    except Exception as e:
        print(f"❌ Error migrating transcript {transcript.id}: {str(e)}")
        return False

def verify_migration(transcript):
    """Verify that a transcript and its questions were migrated correctly"""
    try:
        # Verify transcript
        mongo_transcript = mongo_service.db.transcripts.find_one({'django_id': transcript.id})
        if not mongo_transcript:
            print(f"❌ Verification failed: Transcript {transcript.id} not found in MongoDB")
            return False
            
        # Verify questions
        mongo_questions = list(mongo_service.db.questions.find({'django_transcript_id': transcript.id}))
        if len(mongo_questions) != transcript.questions.count():
            print(f"❌ Verification failed: Question count mismatch for transcript {transcript.id}")
            return False
            
        print(f"✅ Verified migration for transcript: {transcript.title}")
        return True
        
    except Exception as e:
        print(f"❌ Error verifying migration for transcript {transcript.id}: {str(e)}")
        return False

def migrate_all_data():
    """Migrate all transcripts and questions to MongoDB"""
    print("\n=== Starting Migration to MongoDB ===\n")
    
    # Get total counts for progress tracking
    total_transcripts = Transcript.objects.count()
    total_questions = Question.objects.count()
    
    print(f"Found {total_transcripts} transcripts and {total_questions} questions to migrate")
    
    # Create indexes in MongoDB
    mongo_service.db.transcripts.create_index([("django_id", 1)], unique=True)
    mongo_service.db.transcripts.create_index([("user_id", 1)])
    mongo_service.db.transcripts.create_index([("video_id", 1)])
    mongo_service.db.questions.create_index([("django_id", 1)], unique=True)
    mongo_service.db.questions.create_index([("transcript_id", 1)])
    
    # Track migration progress
    successful_transcripts = 0
    successful_verifications = 0
    
    # Migrate each transcript and its questions
    for transcript in Transcript.objects.all():
        print(f"\nMigrating transcript {transcript.id}: {transcript.title}")
        
        if migrate_transcript(transcript):
            successful_transcripts += 1
            
            if verify_migration(transcript):
                successful_verifications += 1
    
    # Print summary
    print("\n=== Migration Summary ===")
    print(f"Total transcripts: {total_transcripts}")
    print(f"Successfully migrated: {successful_transcripts}")
    print(f"Successfully verified: {successful_verifications}")
    print(f"Total questions migrated: {mongo_service.db.questions.count_documents({})}")
    
    if successful_verifications == total_transcripts:
        print("\n✅ Migration completed successfully!")
    else:
        print("\n⚠️ Migration completed with some issues. Please check the logs above.")

if __name__ == "__main__":
    # Ask for confirmation before proceeding
    response = input("This will migrate data to MongoDB. The existing SQLite data will be preserved. Proceed? (y/n): ")
    if response.lower() == 'y':
        migrate_all_data()
    else:
        print("Migration cancelled.") 