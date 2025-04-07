import os
import sys
import django

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.contrib.auth.models import User
from api.models import Transcript, Question

def check_data():
    print("\n=== Current Data in SQLite Database ===\n")
    
    # Check Users
    users = User.objects.all()
    print(f"Total Users: {users.count()}")
    for user in users:
        print(f"- User: {user.email}")
    
    print("\n=== Transcripts ===")
    transcripts = Transcript.objects.all()
    print(f"Total Transcripts: {transcripts.count()}")
    
    for transcript in transcripts:
        print(f"\nTranscript: {transcript.title}")
        print(f"- ID: {transcript.id}")
        print(f"- Video ID: {transcript.video_id}")
        print(f"- User: {transcript.user.email}")
        print(f"- Language: {transcript.language}")
        print(f"- Created: {transcript.created_at}")
        print(f"- Questions: {transcript.questions.count()}")
        
        # Show sample questions for each transcript
        questions = transcript.questions.all()
        if questions:
            print("\nSample Questions:")
            for question in questions[:2]:  # Show first 2 questions as sample
                print(f"- Type: {question.question_type}")
                print(f"- Question: {question.question_text[:100]}...")
                print(f"- Answer: {question.answer[:100]}...")
                print()

if __name__ == "__main__":
    check_data() 