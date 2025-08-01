#!/usr/bin/env python3
"""
Script to create database indexes for better query performance.
"""

import os
import sys
import django
from datetime import datetime

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from api.services.mongo_service import mongo_service

def create_indexes():
    """Create database indexes for better performance"""
    print("🚀 Creating database indexes...")
    
    try:
        db = mongo_service.db
        
        # Create indexes for curated_videos collection
        curated_videos = db.curated_videos
        
        # Index for topic and difficulty filtering
        print("📊 Creating index on topic and difficulty...")
        curated_videos.create_index([("topic", 1), ("difficulty", 1)])
        
        # Index for sorting by creation date
        print("📅 Creating index on created_at...")
        curated_videos.create_index("created_at")
        
        # Text index for search functionality (title and description)
        print("🔍 Creating text index for search...")
        curated_videos.create_index([
            ("title", "text"), 
            ("description", "text")
        ])
        
        # Index for video_id lookups
        print("🎬 Creating index on video_id...")
        curated_videos.create_index("video_id", unique=True)
        
        # Index for duration filtering
        print("⏱️ Creating index on duration...")
        curated_videos.create_index("duration")
        
        print("✅ All indexes created successfully!")
        
        # List all indexes
        print("\n📋 Current indexes on curated_videos collection:")
        indexes = curated_videos.list_indexes()
        for index in indexes:
            print(f"   - {index['name']}: {index['key']}")
            
    except Exception as e:
        print(f"❌ Error creating indexes: {str(e)}")
        raise

if __name__ == "__main__":
    create_indexes() 