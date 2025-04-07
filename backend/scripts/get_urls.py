import os
import sys
import yt_dlp
from datetime import datetime

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

import django
django.setup()

from api.services.mongo_service import mongo_service

PLAYLIST_URL = "https://www.youtube.com/playlist?list=PL48CaRIHVwhX-QW3yVgbbKUhZYPKpv0wY"

def get_urls_from_playlist(playlist_url):
    """Fetch video URLs from a YouTube playlist"""
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'dump_single_json': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(playlist_url, download=False)
        return [
            {
                'url': entry['url'],
                'video_id': entry['id'],
                'title': entry.get('title', ''),
                'duration': entry.get('duration', 0),
                'fetched_at': datetime.utcnow()
            }
            for entry in info['entries']
        ]

def get_existing_video_ids():
    """Get list of video IDs already in MongoDB"""
    return set(doc['video_id'] for doc in mongo_service.db.youtube_videos.find({}, {'video_id': 1}))

def save_new_videos(videos):
    """Save new videos to MongoDB"""
    existing_ids = get_existing_video_ids()
    new_videos = [video for video in videos if video['video_id'] not in existing_ids]
    
    if new_videos:
        mongo_service.db.youtube_videos.insert_many(new_videos)
        return len(new_videos)
    return 0

def main():
    print("🔍 Fetching playlist URLs...")
    try:
        # Create index on video_id if it doesn't exist
        mongo_service.db.youtube_videos.create_index('video_id', unique=True)
        
        # Fetch and process videos
        videos = get_urls_from_playlist(PLAYLIST_URL)
        new_count = save_new_videos(videos)
        
        total_count = mongo_service.db.youtube_videos.count_documents({})
        
        if new_count > 0:
            print(f"✅ Added {new_count} new videos to MongoDB.")
        else:
            print("✅ No new videos found.")
            
        print(f"📊 Total videos in database: {total_count}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main() 