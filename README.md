# Hindi Question-Answer Generation System

A web application that automatically generates Hindi questions and answers from YouTube videos. The system processes Hindi YouTube videos, extracts transcripts, and uses AI to generate meaningful questions and answers, creating an interactive learning resource.

## Features

- 🎥 YouTube video transcript extraction
- 🤖 AI-powered question generation
- 👥 User authentication and management
- 💾 Transcript and Q&A storage
- ⚡ Real-time processing
- 📱 Responsive web interface

## Tech Stack

### Backend
- Django (Python web framework)
- Django REST Framework
- yt-dlp (YouTube video processing)
- youtube-transcript-api
- DeepSeek API (for question generation)
- MongoDB Atlas (Database)

### Frontend
- React.js
- Material-UI (MUI)
- Axios

### Infrastructure
- Render.com for deployment
- MongoDB Atlas 
- Automated job scheduling via Cron Jobs


## Setup

### Prerequisites
- Python 3.8+
- Node.js 14+
- MongoDB Atlas
- DeepSeek API key

### Local Development

1. Clone the repository:
```bash
git clone <repository-url>
cd Hindi-QA
```

2. Set up the Python virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Set up the database:
```bash
python manage.py migrate
python manage.py createsuperuser
```

5. Install frontend dependencies:
```bash
cd frontend
npm install
```

6. Run the development servers:

Backend:
```bash
python manage.py runserver
```

Frontend:
```bash
cd frontend
npm start
```

## Usage

1. Log in to the application
2. Paste a YouTube URL or select from available playlists
3. The system will automatically:
   - Extract the video transcript
   - Generate questions and answers
   - Store them in the database
4. View and interact with the generated Q&A pairs

## Automated Processing

The system uses Render.com's Cron Jobs to automatically process videos:

```bash
python manage.py process_youtube_videos --urls-file all_urls.json --user-id YOUR_USER_ID
```

You can also process a specific playlist:
```bash
python manage.py process_youtube_videos --playlist-url "YOUR_PLAYLIST_URL" --user-id YOUR_USER_ID
```

## API Endpoints

### Transcripts
- `GET /api/transcripts/` - List all transcripts
- `POST /api/transcripts/create_from_video/` - Create new transcript from video
- `GET /api/transcripts/{id}/` - Get specific transcript
- `DELETE /api/transcripts/{id}/` - Delete transcript
- `POST /api/transcripts/{id}/toggle_favorite/` - Toggle favorite status

### Authentication
- `POST /api/auth/login/` - User login
- `POST /api/auth/register/` - User registration
- `POST /api/auth/logout/` - User logout

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Acknowledgments

- YouTube Data API
- DeepSeek API for question generation
- All open-source libraries used in this project
