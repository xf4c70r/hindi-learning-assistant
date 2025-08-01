#!/usr/bin/env python3
"""
Script to import curated videos into MongoDB for the agentic learning system.
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
from curated_videos_data import CURATED_VIDEOS_DATA, SUMMARY

def import_curated_videos():
    """Import curated videos into MongoDB"""
    print("🚀 Starting curated videos import...")
    
    try:
        # Get the curated videos from the data
        videos = CURATED_VIDEOS_DATA.get("curated_videos", [])
        
        if not videos:
            print("❌ No videos found in the data")
            return
        
        print(f"📹 Found {len(videos)} videos to import")
        
        # Import each video
        imported_count = 0
        skipped_count = 0
        
        for video_data in videos:
            video_id = video_data.get("video_id")
            
            # Check if video already exists
            existing_video = mongo_service.get_curated_video_by_id(video_id)
            
            if existing_video:
                print(f"⏭️  Skipping {video_id} - already exists")
                skipped_count += 1
                continue
            
            # Import the video
            try:
                result = mongo_service.save_curated_video(video_data)
                print(f"✅ Imported: {video_data.get('title', video_id)}")
                imported_count += 1
            except Exception as e:
                print(f"❌ Failed to import {video_id}: {str(e)}")
        
        print(f"\n📊 Import Summary:")
        print(f"   ✅ Successfully imported: {imported_count}")
        print(f"   ⏭️  Skipped (already exists): {skipped_count}")
        print(f"   📹 Total processed: {len(videos)}")
        
        if imported_count > 0:
            print(f"\n🎉 Successfully imported {imported_count} curated videos!")
        else:
            print(f"\nℹ️  No new videos were imported (all already exist)")
            
    except Exception as e:
        print(f"❌ Error during import: {str(e)}")
        raise

def create_sample_learning_paths():
    """Create sample learning paths based on the curated videos"""
    print("\n🛤️  Creating sample learning paths...")
    
    try:
        # Sample learning paths
        learning_paths = [
            {
                "name": "Beginner Daily Life",
                "description": "Learn essential Hindi for everyday situations",
                "target_level": "beginner",
                "topic": "daily_life",
                "videos": [
                    {
                        "video_id": "dGn9LOdafXA",
                        "order": 1,
                        "estimated_duration": 7,
                        "learning_objectives": [
                            "Learn shop vocabulary",
                            "Practice polite requests",
                            "Understand bargaining culture"
                        ]
                    },
                    {
                        "video_id": "G9A0pUWm5RE",
                        "order": 2,
                        "estimated_duration": 10,
                        "learning_objectives": [
                            "Order food in restaurants",
                            "Ask for the bill",
                            "Use polite forms of address"
                        ]
                    }
                ],
                "total_duration": 17,
                "prerequisites": ["basic greetings", "numbers 1-10"],
                "learning_outcomes": [
                    "Confidently shop in Hindi",
                    "Order food at restaurants",
                    "Use polite language with vendors"
                ]
            }
        ]
        
        created_count = 0
        for path_data in learning_paths:
            try:
                result = mongo_service.save_learning_path(path_data)
                print(f"✅ Created learning path: {path_data.get('name')}")
                created_count += 1
            except Exception as e:
                print(f"❌ Failed to create learning path: {str(e)}")
        
        print(f"🛤️  Created {created_count} learning paths")
        
    except Exception as e:
        print(f"❌ Error creating learning paths: {str(e)}")
        raise

def main():
    """Main function to run the import process"""
    print("=" * 60)
    print("🎯 CURATED VIDEOS IMPORT SCRIPT")
    print("=" * 60)
    
    # Show dataset summary
    print(f"📊 Dataset Summary:")
    print(f"   📹 Total videos: {SUMMARY['total_videos']}")
    print(f"   🎯 Topics: {', '.join(SUMMARY['topic_distribution'].keys())}")
    print(f"   📈 Difficulty: {', '.join(SUMMARY['difficulty_distribution'].keys())}")
    print(f"   ⭐ Average rating: {SUMMARY['average_rating']}")
    print()
    
    try:
        # Import curated videos
        import_curated_videos()
        
        # Create sample learning paths
        create_sample_learning_paths()
        
        print("\n" + "=" * 60)
        print("🎉 IMPORT COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Import failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 