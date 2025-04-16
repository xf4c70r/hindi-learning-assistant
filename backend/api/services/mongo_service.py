import os
import certifi
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
from urllib.parse import quote_plus
from bson import ObjectId

# Load environment variables
load_dotenv()

class MongoService:
    _instance = None
    _client = None
    _db = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoService, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._client is None:
            self._connect()

    def _connect(self):
        """Connect to MongoDB"""
        try:
            uri = os.environ.get('MONGODB_URI')
            db_name = os.environ.get('MONGODB_NAME', 'hindi_qa_db')
            
            if not uri:
                raise ValueError("MONGODB_URI environment variable is not set")

            print(f"Attempting to connect to MongoDB with URI: {uri[:20]}...")
            
            # Connect with SSL certificate verification
            self._client = MongoClient(
                uri,
                tlsCAFile=certifi.where()
            )
            self._db = self._client[db_name]
            
            # Test the connection
            self._client.admin.command('ping')
            print(f"Successfully connected to MongoDB Atlas")
        except Exception as e:
            print(f"Error connecting to MongoDB: {str(e)}")
            raise

    @property
    def db(self):
        """Get database instance"""
        return self._db

    def save_qa_pair(self, transcript_id, qa_data):
        """Save QA pair to MongoDB"""
        collection = self._db.qa_pairs
        qa_data['transcript_id'] = transcript_id
        return collection.insert_one(qa_data)

    def get_qa_pairs(self, transcript_id=None):
        """Get QA pairs, optionally filtered by transcript_id"""
        collection = self._db.qa_pairs
        query = {'transcript_id': transcript_id} if transcript_id else {}
        return list(collection.find(query))

    def save_transcript(self, user_id, video_id, content, language='hi'):
        """Save transcript to MongoDB"""
        try:
            collection = self._db.transcripts
            data = {
                'user_id': user_id,
                'video_id': video_id,
                'content': content,
                'language': language,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
                'is_favorite': False
            }
            result = collection.insert_one(data)
            print(f"Successfully saved transcript to MongoDB with ID: {result.inserted_id}")
            return result
        except Exception as e:
            print(f"Error saving transcript to MongoDB: {str(e)}")
            raise

    def get_transcripts(self, user_id=None):
        """Get transcripts, optionally filtered by user_id"""
        try:
            collection = self._db.transcripts
            query = {'user_id': user_id} if user_id else {}
            transcripts = list(collection.find(query))
            
            # Convert ObjectIds to strings
            for transcript in transcripts:
                transcript['id'] = str(transcript['_id'])
            
            return transcripts
        except Exception as e:
            print(f"Error getting transcripts from MongoDB: {str(e)}")
            raise

    def get_transcript_by_user_and_video(self, user_id, video_id):
        """Get transcript by user_id and video_id"""
        try:
            collection = self._db.transcripts
            transcript = collection.find_one({
                'user_id': user_id,
                'video_id': video_id
            })
            if transcript:
                transcript['id'] = str(transcript['_id'])
            return transcript
        except Exception as e:
            print(f"Error getting transcript from MongoDB: {str(e)}")
            raise

    def toggle_transcript_favorite(self, transcript_id, user_id):
        """Toggle favorite status of a transcript"""
        try:
            collection = self._db.transcripts
            transcript = collection.find_one({
                '_id': ObjectId(transcript_id),
                'user_id': user_id
            })
            
            if not transcript:
                return None
                
            # Toggle the is_favorite field
            is_favorite = not transcript.get('is_favorite', False)
            collection.update_one(
                {'_id': ObjectId(transcript_id)},
                {
                    '$set': {
                        'is_favorite': is_favorite,
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            
            # Return updated transcript
            transcript['is_favorite'] = is_favorite
            transcript['id'] = str(transcript['_id'])
            return transcript
        except Exception as e:
            print(f"Error toggling favorite in MongoDB: {str(e)}")
            raise

# Create singleton instance
mongo_service = MongoService() 