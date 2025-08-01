#!/usr/bin/env python3
"""
Test specific videos that were failing
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.youtube_utils import get_transcript, check_video_captions
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_video(video_id, description):
    """Test a specific video."""
    print(f"\n{'='*50}")
    print(f"Testing: {description}")
    print(f"Video ID: {video_id}")
    print(f"{'='*50}")
    
    try:
        # Check if captions are available
        print("1. Checking captions availability...")
        available_languages = check_video_captions(video_id)
        print(f"   Available languages: {available_languages}")
        
        if not available_languages:
            print("   ❌ No captions available")
            return False
        
        # Try to get transcript
        print("2. Fetching transcript...")
        transcript_data, language = get_transcript(video_id)
        print(f"   ✅ Successfully fetched {language} transcript with {len(transcript_data)} entries")
        
        # Show first entry
        if transcript_data:
            first_entry = transcript_data[0]
            print(f"   First entry: {first_entry['text'][:100]}...")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

def main():
    """Test the specific videos."""
    print("Testing Specific Videos with VPN")
    print("=" * 50)
    
    # Test videos
    test_videos = [
        ("jNQXAC9IVRw", "First YouTube video (Me at the zoo) - Known working"),
        ("UayIEps9Y70", "First problematic video"),
        ("cgNhX6KO3xo", "Second problematic video (Hindi auto-generated captions)")
    ]
    
    results = []
    
    for video_id, description in test_videos:
        success = test_video(video_id, description)
        results.append(success)
        print(f"   {'✅ SUCCESS' if success else '❌ FAILED'}")
    
    # Summary
    print(f"\n{'='*50}")
    print("SUMMARY")
    print(f"{'='*50}")
    
    for i, (video_id, description) in enumerate(test_videos):
        status = "✅ PASS" if results[i] else "❌ FAIL"
        print(f"{description}: {status}")
    
    passed = sum(results)
    total = len(results)
    print(f"\nOverall: {passed}/{total} videos worked")
    
    if passed == total:
        print("🎉 All videos worked! Your VPN is working perfectly.")
    elif passed > 0:
        print("⚠️  Some videos worked. The VPN is helping but some videos might still be blocked.")
    else:
        print("❌ No videos worked. The VPN might not be sufficient.")

if __name__ == "__main__":
    main() 