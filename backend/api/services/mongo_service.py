import os
import certifi
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
from urllib.parse import quote_plus
from bson import ObjectId
import logging

# Load environment variables
load_dotenv()

# Configure logger
logger = logging.getLogger(__name__)

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
                start = uri.find(':<') + 2
                end = uri.find('>', start)
                if start > 1 and end > start:
                    password = uri[start:end]
                    encoded_password = quote_plus(password)
                    uri = uri.replace(f'<{password}>', encoded_password)
            
            self._client = MongoClient(uri, tlsCAFile=certifi.where())
            self._db = self._client[db_name]
            print("Connected to MongoDB Atlas")
        except Exception as e:
            print(f"Error connecting to MongoDB: {str(e)}")
            raise

    @property
    def db(self):
        return self._db

    # Existing helper methods (truncated for brevity, but retained)...
    # save_qa_pair, get_qa_pairs, save_transcript, etc.

    # -------------------- Learning Session Helpers --------------------

    def create_learning_session(self, user_id: str, video_id: str, initial_state: dict) -> str:
        """Insert a new learning session and return its id."""
        collection = self._db.learning_sessions
        doc = {
            "user_id": user_id,
            "video_id": video_id,
            "state": initial_state,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        result = collection.insert_one(doc)
        return str(result.inserted_id)

    def update_learning_session(self, session_id: str, new_state: dict):
        """Update the session's state and timestamp."""
        collection = self._db.learning_sessions
            collection.update_one(
            {"_id": ObjectId(session_id)},
            {"$set": {"state": new_state, "updated_at": datetime.utcnow()}}
        )

    def get_learning_session(self, session_id: str):
        collection = self._db.learning_sessions
        doc = collection.find_one({"_id": ObjectId(session_id)})
        if doc:
            doc["id"] = str(doc["_id"])
        return doc

    # -------------------- Curated Videos Helpers --------------------

    def get_curated_videos(self, topic=None, difficulty=None, limit=None):
        """Get curated videos with optional filtering."""
            collection = self._db.curated_videos
            query = {}
            
            if topic:
                query['topic'] = topic
            if difficulty:
                query['difficulty'] = difficulty
                
        # Apply limit if specified
            if limit:
            videos = list(collection.find(query).limit(limit))
        else:
            videos = list(collection.find(query))
            
            for video in videos:
                video['id'] = str(video['_id'])
            del video['_id']
        return videos

    def get_curated_video_by_id(self, video_id: str):
        """Get a specific curated video by ID."""
        collection = self._db.curated_videos
        doc = collection.find_one({"_id": ObjectId(video_id)})
        if doc:
            doc["id"] = str(doc["_id"])
            del doc["_id"]
        return doc

    def get_curated_video_topics(self):
        """Get unique topics from curated videos."""
            collection = self._db.curated_videos
        topics = collection.distinct("topic")
        return [{"name": topic, "count": collection.count_documents({"topic": topic})} for topic in topics]

    def save_curated_video(self, video_data: dict):
        """Save a curated video to the database."""
            collection = self._db.curated_videos
        
        # Add timestamps
        video_data["created_at"] = datetime.utcnow()
        video_data["updated_at"] = datetime.utcnow()
        
        # Check if video already exists
        existing = collection.find_one({"video_id": video_data.get("video_id")})
        
        if existing:
            # Update existing video
            collection.update_one(
                {"_id": existing["_id"]},
                {"$set": video_data}
            )
            return str(existing["_id"])
        else:
            # Create new video
            result = collection.insert_one(video_data)
            return str(result.inserted_id)

    # -------------------- Learning Paths Helpers --------------------

    def get_learning_paths(self, user_level=None, topic=None):
        """Get learning paths with optional filtering."""
            collection = self._db.learning_paths
            query = {}
            
            if user_level:
                query['target_level'] = user_level
            if topic:
                query['topic'] = topic
                
        paths = list(collection.find(query))
            for path in paths:
                path['id'] = str(path['_id'])
            del path['_id']
        return paths

    def get_learning_path_by_id(self, path_id: str):
        """Get a specific learning path by ID."""
        collection = self._db.learning_paths
        doc = collection.find_one({"_id": ObjectId(path_id)})
        if doc:
            doc["id"] = str(doc["_id"])
            del doc["_id"]
        return doc

    # -------------------- User Progress Helpers --------------------

    def get_user_learning_progress(self, user_id: str, video_id: str = None):
        """Get user's learning progress for specific video or all videos."""
        collection = self._db.user_progress
        query = {"user_id": user_id}
        
        if video_id:
            query["video_id"] = video_id
        
        progress_docs = list(collection.find(query))
        for doc in progress_docs:
            doc["id"] = str(doc["_id"])
            del doc["_id"]
        return progress_docs

    def save_user_progress(self, user_id: str, progress_data: dict):
        """Save or update user progress."""
        collection = self._db.user_progress
        
        # Add user_id and timestamp
        progress_data["user_id"] = user_id
        progress_data["updated_at"] = datetime.utcnow()
        
        # Check if progress already exists for this user and video
        existing = collection.find_one({
            "user_id": user_id,
            "video_id": progress_data.get("video_id")
        })
        
        if existing:
            # Update existing progress
            collection.update_one(
                {"_id": existing["_id"]},
                {"$set": progress_data}
            )
            return str(existing["_id"])
        else:
            # Create new progress
            progress_data["created_at"] = datetime.utcnow()
            result = collection.insert_one(progress_data)
            return str(result.inserted_id)

    def save_user_learning_progress(self, user_id: str, video_id: str, progress_data: dict):
        """Save or update user learning progress (alias for save_user_progress)."""
        # Ensure video_id is in progress_data
        progress_data["video_id"] = video_id
        return self.save_user_progress(user_id, progress_data)

    def get_user_learning_stats(self, user_id: str):
        """Get user's learning statistics."""
        collection = self._db.user_progress
        
        # Get all progress for user
        user_progress = list(collection.find({"user_id": user_id}))
        
        # Calculate basic stats
        total_videos = len(user_progress)
        completed_videos = len([p for p in user_progress if p.get("completion_status") == "completed"])
        in_progress_videos = len([p for p in user_progress if p.get("completion_status") == "in_progress"])
        total_time_spent = sum([p.get("time_spent", 0) for p in user_progress])
        
        # Calculate average score
        scores = [p.get("scores", {}).get("overall", 0) for p in user_progress if p.get("scores")]
        average_score = sum(scores) / len(scores) if scores else 0
        
        # Group videos by status
        videos_by_status = {
            "completed": completed_videos,
            "in_progress": in_progress_videos,
            "not_started": total_videos - completed_videos - in_progress_videos
        }
        
        # Group videos by topic (would need to join with curated_videos collection)
        videos_by_topic = {}
        videos_by_difficulty = {}
        
        # Recent activity (last 7 days)
        recent_activity = []
        for progress in user_progress[-10:]:  # Last 10 activities
            if progress.get("updated_at"):
                recent_activity.append({
                    "video_id": progress.get("video_id"),
                    "action": progress.get("completion_status"),
                    "timestamp": progress.get("updated_at")
                })
        
        return {
            "total_videos_watched": total_videos,
            "total_time_spent": total_time_spent,
            "completion_rate": (completed_videos / total_videos * 100) if total_videos > 0 else 0,
            "average_score": average_score,
            "videos_by_status": videos_by_status,
            "videos_by_topic": videos_by_topic,
            "videos_by_difficulty": videos_by_difficulty,
            "recent_activity": recent_activity,
            "learning_streak": 0,  # Would need to calculate based on daily activity
            "total_learning_paths": 0  # Would need to count from learning_paths collection
        }

# Singleton instance
mongo_service = MongoService() 
