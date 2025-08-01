#!/usr/bin/env python3
"""
Test script to debug YouTube caption fetching issues
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.youtube_utils import check_video_captions, get_transcript_with_retry
from youtube_transcript_api import YouTubeTranscriptApi
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_video_captions(video_id):
    """Test caption fetching for a specific video ID."""
    print(f"\n{'='*50}")
    print(f"Testing video ID: {video_id}")
    print(f"{'='*50}")
    
    try:
        # Test 1: Check available languages
        print("1. Checking available languages...")
        available_languages = check_video_captions(video_id)
        print(f"   Available languages: {available_languages}")
        
        if not available_languages:
            print("   ❌ No languages available")
            return False
        
        # Test 2: Try to get transcript list
        print("2. Getting transcript list...")
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        print(f"   ✅ Successfully got transcript list")
        
        # Test 3: Try to find Hindi transcript
        print("3. Looking for Hindi transcript...")
        try:
            hindi_transcript = transcript_list.find_transcript(['hi'])
            print(f"   ✅ Found Hindi transcript")
            
            # Test 4: Try to fetch the actual transcript
            print("4. Fetching transcript data...")
            transcript_data = hindi_transcript.fetch()
            print(f"   ✅ Successfully fetched transcript with {len(transcript_data)} entries")
            
            # Show first few entries
            if transcript_data:
                print(f"   First entry: {transcript_data[0]}")
                print(f"   Text preview: {transcript_data[0]['text'][:100]}...")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Error with Hindi transcript: {str(e)}")
            
            # Try English as fallback
            print("5. Trying English transcript as fallback...")
            try:
                english_transcript = transcript_list.find_transcript(['en'])
                print(f"   ✅ Found English transcript")
                
                transcript_data = english_transcript.fetch()
                print(f"   ✅ Successfully fetched English transcript with {len(transcript_data)} entries")
                
                if transcript_data:
                    print(f"   First entry: {transcript_data[0]}")
                    print(f"   Text preview: {transcript_data[0]['text'][:100]}...")
                
                return True
                
            except Exception as e2:
                print(f"   ❌ Error with English transcript: {str(e2)}")
                return False
    
    except Exception as e:
        print(f"   ❌ General error: {str(e)}")
        return False

def main():
    """Test the problematic video IDs."""
    video_ids = ['UayIEps9Y70', 'cgNhX6KO3xo']
    
    print("YouTube Caption Fetching Debug Test")
    print("=" * 50)
    
    for video_id in video_ids:
        success = test_video_captions(video_id)
        if success:
            print(f"✅ Video {video_id}: SUCCESS")
        else:
            print(f"❌ Video {video_id}: FAILED")
    
    print(f"\n{'='*50}")
    print("Test completed!")

if __name__ == "__main__":
    main() 