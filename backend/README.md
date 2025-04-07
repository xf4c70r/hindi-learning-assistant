# Hindi YouTube Video QA Backend

A Django REST API backend for generating and managing Q&A pairs from Hindi YouTube video transcripts.

## Features

- User Authentication (Token-based)
- YouTube Transcript Extraction
- Multi-language Support (Hindi/English)
- Question Generation from Transcripts
- Favorites Management
- RESTful API Design

## Tech Stack

- Django 4.2.0
- Django REST Framework 3.14.0
- YouTube Transcript API
- SQLite Database (Development)
- Token Authentication

## Project Structure

```
backend/
├── api/                    # API endpoints and views
│   ├── views.py           # API view implementations
│   ├── urls.py            # API URL routing
│   └── serializers.py     # Data serializers
├── core/                  # Core business logic
│   ├── models.py          # Database models
│   └── youtube_utils.py   # YouTube transcript utilities
├── qa_engine/            # ML model integration
│   └── ml_model.py       # Question generation model
└── backend/              # Project settings
    ├── settings.py       # Django settings
    └── urls.py           # Main URL routing
```

## API Endpoints

### Authentication

#### POST /api/auth/signup/

Create a new user account.

```json
{
  "username": "string",
  "password": "string",
  "email": "string"
}
```

Response:

```json
{
  "message": "User created successfully",
  "token": "string"
}
```

#### POST /api/auth/login/

Login with existing credentials.

```json
{
  "username": "string",
  "password": "string"
}
```

Response:

```json
{
  "message": "Login successful",
  "token": "string"
}
```

### Transcripts

#### POST /api/transcripts/

Extract transcript from YouTube video.

```json
{
  "youtube_url": "string"
}
```

Response:

```json
{
  "id": "integer",
  "youtube_url": "string",
  "title": "string",
  "content": "string",
  "language": "string",
  "created_at": "datetime",
  "user": {
    "id": "integer",
    "username": "string",
    "email": "string"
  },
  "questions": []
}
```

#### GET /api/transcripts/

Get all transcripts for the authenticated user.

### Questions

#### POST /api/qa/generate/

Generate questions for a transcript.

```json
{
  "transcript_id": "integer"
}
```

Response:

```json
[
  {
    "id": "integer",
    "question_text": "string",
    "correct_answer": "string",
    "options": ["string"],
    "created_at": "datetime"
  }
]
```

### Favorites

#### POST /api/favorites/

Add a transcript to favorites.

```json
{
  "transcript_id": "integer"
}
```

#### GET /api/favorites/

Get all favorite transcripts for the authenticated user.

## Setup Instructions

1. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

4. Create superuser (optional):

```bash
python manage.py createsuperuser
```

5. Run the development server:

```bash
python manage.py runserver
```

## Authentication

The API uses token-based authentication. Include the token in the request header:

```
Authorization: Token <your-token>
```

## YouTube Transcript Features

- Automatic language detection
- Fallback to English if Hindi not available
- Support for manual and auto-generated transcripts
- Transcript text formatting and cleaning

## ML Model Integration

The `qa_engine` app provides a placeholder for ML model integration:

- `QAModel` class in `ml_model.py`
- Ready for real model implementation
- Supports question generation with multiple choice options

## Testing

Use the provided test script to verify API functionality:

```bash
python test_api.py
```

The script tests:

- User authentication
- Transcript extraction
- Question generation
- Error handling

## Error Handling

The API implements comprehensive error handling:

- Invalid YouTube URLs
- Missing transcripts
- Authentication errors
- Model processing errors

## Future Improvements

1. Add video title extraction
2. Implement real ML model integration
3. Add transcript search functionality
4. Support for more languages
5. Add user preferences
6. Implement rate limiting
7. Add caching for transcripts

## Security Considerations

1. Token-based authentication
2. CORS configuration for frontend
3. Input validation
4. Error message sanitization
5. Django security middleware enabled
