import os
import certifi
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
from urllib.parse import quote_plus

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
            uri = os.getenv('MONGODB_URI')
            db_name = os.getenv('MONGODB_NAME', 'hindi_qa_db')
            
            if not uri:
                raise ValueError("MONGODB_URI environment variable is not set")

            # Handle URL encoding of username and password if needed
            if '<' in uri and '>' in uri:
                # Extract and encode password
                start = uri.find(':<') + 2
                end = uri.find('>', start)
                if start > 1 and end > start:
                    password = uri[start:end]
                    encoded_password = quote_plus(password)
                    uri = uri.replace(f'<{password}>', encoded_password)
            
            # Connect with SSL certificate verification
            self._client = MongoClient(
                uri,
                tlsCAFile=certifi.where()
            )
            self._db = self._client[db_name]
            print(f"Connected to MongoDB Atlas")
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
                'updated_at': datetime.utcnow()
            }
            result = collection.insert_one(data)
            print(f"Successfully saved transcript to MongoDB with ID: {result.inserted_id}")
            return result
        except Exception as e:
            print(f"Error saving transcript to MongoDB: {str(e)}")
            raise

    def get_transcripts(self, user_id=None):
        """Get transcripts, optionally filtered by user_id"""
        collection = self._db.transcripts
        query = {'user_id': user_id} if user_id else {}
        return list(collection.find(query))

# Create singleton instance
mongo_service = MongoService() 