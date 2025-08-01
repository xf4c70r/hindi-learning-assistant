#!/usr/bin/env python3
"""
Test script to check MongoDB connection and collections
"""

import os
import sys
import django

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from api.services.mongo_service import mongo_service

def test_mongo_connection():
    """Test MongoDB connection and basic operations"""
    print("🔍 Testing MongoDB connection...")
    
    try:
        # Test connection
        db = mongo_service.db
        print(f"✅ Connected to database: {db.name}")
        
        # List collections
        collections = db.list_collection_names()
        print(f"📚 Available collections: {collections}")
        
        # Test curated videos
        print("\n🎬 Testing curated videos...")
        try:
            videos = mongo_service.get_curated_videos()
            print(f"✅ Found {len(videos)} curated videos")
            if videos:
                print(f"   Sample video: {videos[0].get('title', 'No title')}")
        except Exception as e:
            print(f"❌ Error getting curated videos: {e}")
        
        # Test topics
        print("\n📋 Testing video topics...")
        try:
            topics = mongo_service.get_curated_video_topics()
            print(f"✅ Found {len(topics)} topics")
            for topic in topics[:3]:  # Show first 3
                print(f"   - {topic['name']}: {topic['count']} videos")
        except Exception as e:
            print(f"❌ Error getting topics: {e}")
        
        # Test learning paths
        print("\n🛤️  Testing learning paths...")
        try:
            paths = mongo_service.get_learning_paths()
            print(f"✅ Found {len(paths)} learning paths")
        except Exception as e:
            print(f"❌ Error getting learning paths: {e}")
        
        # Test user progress (should be empty for new users)
        print("\n📊 Testing user progress...")
        try:
            progress = mongo_service.get_user_learning_progress("test_user")
            print(f"✅ User progress method works (found {len(progress)} records)")
        except Exception as e:
            print(f"❌ Error getting user progress: {e}")
        
        print("\n🎉 MongoDB connection test completed!")
            
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_mongo_connection() 