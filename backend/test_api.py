import requests
import json

BASE_URL = 'http://localhost:8000/api'

def test_api():
    # Login to get token
    login_data = {
        'email': 'test@example.com',
        'password': 'testpassword'
    }
    
    print("Logging in...")
    response = requests.post(f'{BASE_URL}/auth/login/', json=login_data)
    print(f"Login response: {response.text}")
    
    if response.status_code != 200:
        print("Login failed!")
        return
        
    # Get the token
    token = response.json()['access']
    
    # Set up headers for authenticated requests
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    # Test question generation
    print("\nTesting question generation...")
    transcript_id = 1  # Replace with an actual transcript ID
    question_data = {
        'question_type': 'novice'
    }
    
    response = requests.post(
        f'{BASE_URL}/transcripts/{transcript_id}/questions/generate/',
        headers=headers,
        json=question_data
    )
    
    print(f"Question generation response status: {response.status_code}")
    print(f"Response: {response.text}")

if __name__ == '__main__':
    test_api() 