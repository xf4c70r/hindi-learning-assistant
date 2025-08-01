#!/usr/bin/env python3
"""
Comprehensive test to check YouTube Transcript API status
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from youtube_transcript_api import YouTubeTranscriptApi
import logging
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_basic_api_connectivity():
    """Test basic API connectivity with a known working video."""
    print("\n" + "="*60)
    print("TEST 1: Basic API Connectivity")
    print("="*60)
    
    # Test with a popular video that definitely has captions
    test_video_id = "dQw4w9WgXcQ"  # Rick Astley - Never Gonna Give You Up (has captions)
    
    try:
        print(f"Testing with video ID: {test_video_id}")
        api = YouTubeTranscriptApi()
        transcript_list = api.list(test_video_id)
        available_languages = [t.language_code for t in transcript_list]
        print(f"✅ API is working! Available languages: {available_languages}")
        
        # Try to fetch English transcript
        try:
            transcript = transcript_list.find_transcript(['en'])
            transcript_data = transcript.fetch()
            print(f"✅ Successfully fetched English transcript with {len(transcript_data)} entries")
            return True
        except Exception as e:
            print(f"❌ Failed to fetch transcript: {str(e)}")
            return False
            
    except Exception as e:
        print(f"❌ API connectivity failed: {str(e)}")
        return False

def test_network_connectivity():
    """Test basic network connectivity to YouTube."""
    print("\n" + "="*60)
    print("TEST 2: Network Connectivity")
    print("="*60)
    
    try:
        import requests
        print("Testing connection to YouTube...")
        
        # Test basic HTTP connection to YouTube
        response = requests.get("https://www.youtube.com", timeout=10)
        print(f"✅ YouTube website accessible (Status: {response.status_code})")
        
        # Test connection to YouTube API endpoints
        response = requests.get("https://www.youtube.com/api/timedtext", timeout=10)
        print(f"✅ YouTube API endpoint accessible (Status: {response.status_code})")
        
        return True
    except Exception as e:
        print(f"❌ Network connectivity issue: {str(e)}")
        return False

def test_rate_limiting():
    """Test if we're being rate limited."""
    print("\n" + "="*60)
    print("TEST 3: Rate Limiting Check")
    print("="*60)
    
    test_video_id = "dQw4w9WgXcQ"
    
    try:
        print("Making multiple rapid requests to check for rate limiting...")
        
        for i in range(3):
            print(f"  Request {i+1}/3...")
            start_time = time.time()
            
            try:
                api = YouTubeTranscriptApi()
                transcript_list = api.list(test_video_id)
                available_languages = [t.language_code for t in transcript_list]
                elapsed = time.time() - start_time
                print(f"    ✅ Success (took {elapsed:.2f}s)")
                
                if i < 2:  # Don't sleep after last request
                    time.sleep(1)  # Small delay between requests
                    
            except Exception as e:
                elapsed = time.time() - start_time
                if "Too Many Requests" in str(e):
                    print(f"    ❌ Rate limited (took {elapsed:.2f}s)")
                    return False
                else:
                    print(f"    ❌ Other error: {str(e)} (took {elapsed:.2f}s)")
                    return False
        
        print("✅ No rate limiting detected")
        return True
        
    except Exception as e:
        print(f"❌ Rate limiting test failed: {str(e)}")
        return False

def test_different_video_types():
    """Test with different types of videos."""
    print("\n" + "="*60)
    print("TEST 4: Different Video Types")
    print("="*60)
    
    # Test videos with different caption types
    test_videos = [
        ("dQw4w9WgXcQ", "Popular video with manual captions"),
        ("jNQXAC9IVRw", "First YouTube video (Me at the zoo)"),
        ("kJQP7kiw5Fk", "Luis Fonsi - Despacito (popular with captions)"),
    ]
    
    results = []
    
    for video_id, description in test_videos:
        print(f"\nTesting: {description} ({video_id})")
        try:
            api = YouTubeTranscriptApi()
            transcript_list = api.list(video_id)
            available_languages = [t.language_code for t in transcript_list]
            print(f"  ✅ Available languages: {available_languages}")
            
            # Try to fetch any available transcript
            if available_languages:
                try:
                    transcript = transcript_list.find_transcript([available_languages[0]])
                    transcript_data = transcript.fetch()
                    print(f"  ✅ Successfully fetched {available_languages[0]} transcript ({len(transcript_data)} entries)")
                    results.append(True)
                except Exception as e:
                    print(f"  ❌ Failed to fetch transcript: {str(e)}")
                    results.append(False)
            else:
                print(f"  ⚠️  No captions available")
                results.append(False)
                
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            results.append(False)
    
    success_count = sum(results)
    print(f"\n📊 Results: {success_count}/{len(test_videos)} videos worked")
    return success_count > 0

def test_problematic_videos():
    """Test the specific videos that were failing."""
    print("\n" + "="*60)
    print("TEST 5: Problematic Videos")
    print("="*60)
    
    problematic_videos = [
        ("UayIEps9Y70", "First problematic video"),
        ("cgNhX6KO3xo", "Second problematic video (Hindi auto-generated captions)")
    ]
    
    for video_id, description in problematic_videos:
        print(f"\nTesting: {description} ({video_id})")
        try:
            api = YouTubeTranscriptApi()
            transcript_list = api.list(video_id)
            available_languages = [t.language_code for t in transcript_list]
            print(f"  Available languages: {available_languages}")
            
            # Try different approaches
            for lang in available_languages[:2]:  # Try first 2 languages
                try:
                    print(f"  Trying language: {lang}")
                    transcript = transcript_list.find_transcript([lang])
                    
                    # Try different fetch methods
                    try:
                        transcript_data = transcript.fetch()
                        print(f"    ✅ Standard fetch successful ({len(transcript_data)} entries)")
                        break
                    except Exception as e1:
                        print(f"    ❌ Standard fetch failed: {str(e1)}")
                        
                        try:
                            transcript_data = transcript.fetch(preserve_formatting=True)
                            print(f"    ✅ Preserve formatting fetch successful ({len(transcript_data)} entries)")
                            break
                        except Exception as e2:
                            print(f"    ❌ Preserve formatting fetch failed: {str(e2)}")
                            
                except Exception as e:
                    print(f"    ❌ Language {lang} failed: {str(e)}")
                    
        except Exception as e:
            print(f"  ❌ General error: {str(e)}")

def main():
    """Run all tests."""
    print("YouTube Transcript API Comprehensive Test")
    print("=" * 60)
    
    tests = [
        ("Basic API Connectivity", test_basic_api_connectivity),
        ("Network Connectivity", test_network_connectivity),
        ("Rate Limiting", test_rate_limiting),
        ("Different Video Types", test_different_video_types),
        ("Problematic Videos", test_problematic_videos)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ Test '{test_name}' crashed: {str(e)}")
            results[test_name] = False
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    passed = sum(results.values())
    total = len(results)
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The API should be working fine.")
    elif passed >= 3:
        print("⚠️  Most tests passed. There might be specific issues with certain videos.")
    else:
        print("❌ Multiple tests failed. There might be a broader issue with the API or network.")

if __name__ == "__main__":
    main() 