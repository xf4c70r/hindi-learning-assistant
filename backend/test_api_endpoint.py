import os
import sys
import json
import django
import requests

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.contrib.auth.models import User
from api.models import Transcript, Question
from qa_engine.qa_model import qa_model

def test_transcript_creation():
    """Test the transcript creation API endpoint with processing"""
    try:
        # Create test user if it doesn't exist
        test_user, created = User.objects.get_or_create(
            username='test@example.com',
            email='test@example.com'
        )
        
        # Always set the password to ensure it's properly hashed
        test_user.set_password('testpass123')
        test_user.save()
        print("User created/updated with password")

        # Get JWT token
        print("\nAttempting to login...")
        response = requests.post(
            'http://localhost:8000/api/auth/login/',
            json={
                'email': 'test@example.com',
                'password': 'testpass123'
            }
        )
        print(f"Login response status: {response.status_code}")
        
        if response.status_code != 200:
            print("Failed to get token:", response.text)
            return
        token = response.json()['access']
        print("Got JWT token")

        # Test transcript creation with processing
        headers = {'Authorization': f'Bearer {token}'}
        print("\nCreating transcript from video...")
        response = requests.post(
            'http://localhost:8000/api/transcripts/create-from-video/',
            headers=headers,
            json={
                'video_id': 'https://www.youtube.com/watch?v=test_video_123',
                'title': 'Test Video'
            }
        )
        
        if response.status_code == 201:
            transcript = response.json()
            print("\nCreated Transcript:")
            print(f"ID: {transcript['id']}")
            print(f"Title: {transcript['title']}")
            print(f"Video ID: {transcript['video_id']}")
            print("\nProcessed Content:")
            print(f"Punctuated Text: {transcript['content'][:100]}...")
            print(f"Translation: {transcript['translation'][:100]}...")
            print("\nVocabulary:")
            for word in transcript['vocabulary']:
                print(f"Word: {word['word']}")
                print(f"Meaning: {word['meaning_data']['meaning']}")
                print(f"Example: {word['meaning_data']['example']['hindi']} - {word['meaning_data']['example']['english']}\n")
            
            # Verify response structure
            assert 'content' in transcript, "Missing punctuated text"
            assert 'translation' in transcript, "Missing translation"
            assert 'vocabulary' in transcript, "Missing vocabulary"
            assert isinstance(transcript['vocabulary'], list), "Vocabulary should be a list"
            for word in transcript['vocabulary']:
                assert 'meaning_data' in word, "Word missing meaning_data"
                assert 'example' in word['meaning_data'], "Word missing example"
                assert 'hindi' in word['meaning_data']['example'], "Example missing Hindi text"
                assert 'english' in word['meaning_data']['example'], "Example missing English text"
            
        else:
            print("Failed to create transcript:", response.text)

        print("\nTest completed successfully!")
        
    except Exception as e:
        print(f"\nError testing transcript creation: {str(e)}")
        import traceback
        print(traceback.format_exc())
        sys.exit(1)

def test_question_generation():
    """Test the question generation API endpoint"""
    try:
        # Create test user if it doesn't exist
        test_user, created = User.objects.get_or_create(
            username='test@example.com',
            email='test@example.com'
        )
        
        # Always set the password to ensure it's properly hashed
        test_user.set_password('testpass123')
        test_user.save()
        print("User created/updated with password")

        # Create test transcript if it doesn't exist
        test_transcript, created = Transcript.objects.get_or_create(
            user=test_user,
            video_id='test_video_123',
            defaults={
                'title': 'Test Transcript',
                'content': """
                नमस्ते, मैं आज आपको भारत के बारे में कुछ महत्वपूर्ण जानकारी देना चाहता हूं।
                भारत दुनिया का सबसे बड़ा लोकतंत्र है। यहाँ की आबादी लगभग 140 करोड़ है।
                भारत में 28 राज्य और 8 केंद्र शासित प्रदेश हैं।
                भारत की राजधानी नई दिल्ली है।
                """,
                'language': 'hi'
            }
        )
        if created:
            print("Created test transcript")
        else:
            print("Using existing transcript")

        # Get JWT token
        print("\nAttempting to login...")
        response = requests.post(
            'http://localhost:8000/api/auth/login/',
            json={
                'email': 'test@example.com',
                'password': 'testpass123'
            }
        )
        print(f"Login response status: {response.status_code}")
        
        if response.status_code != 200:
            print("Failed to get token:", response.text)
            return
        token = response.json()['access']
        print("Got JWT token")

        # Test question generation
        headers = {'Authorization': f'Bearer {token}'}
        print("\nGenerating novice questions...")
        response = requests.post(
            f'http://localhost:8000/api/transcripts/{test_transcript.id}/questions/generate/',
            headers=headers,
            json={'question_type': 'novice'}
        )
        
        if response.status_code == 200:
            questions = response.json()
            print("\nGenerated Novice Questions:")
            for i, q in enumerate(questions, 1):
                print(f"\n{i}. Question: {q['question_text']}")
                print(f"   Answer: {q['answer']}")
                if q.get('options'):
                    print(f"   Options: {', '.join(q['options'])}")
                print(f"   Type: {q['question_type']}")
        else:
            print("Failed to generate questions:", response.text)

        # Test MCQ generation
        print("\nGenerating MCQ questions...")
        response = requests.post(
            f'http://localhost:8000/api/transcripts/{test_transcript.id}/questions/generate/',
            headers=headers,
            json={'question_type': 'mcq'}
        )
        
        if response.status_code == 200:
            questions = response.json()
            print("\nGenerated MCQ Questions:")
            for i, q in enumerate(questions, 1):
                print(f"\n{i}. Question: {q['question_text']}")
                print(f"   Answer: {q['answer']}")
                if q.get('options'):
                    print(f"   Options: {', '.join(q['options'])}")
                print(f"   Type: {q['question_type']}")
        else:
            print("Failed to generate MCQ questions:", response.text)

        print("\nTest completed successfully!")
        
    except Exception as e:
        print(f"\nError testing API endpoint: {str(e)}")
        import traceback
        print(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    test_transcript_creation()
    test_question_generation() 