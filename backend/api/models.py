# We no longer need Django models as we're using MongoDB
# This file can be empty or contain documentation about our MongoDB schema

"""
MongoDB Schema Documentation

Collections:

1. transcripts
{
    '_id': ObjectId,
    'user_id': str,
    'video_id': str,
    'title': str,
    'content': str,
    'language': str,
    'created_at': datetime,
    'updated_at': datetime,
    'is_favorite': bool,
    'glossary': {
        'glossary': [
            {
                'word': str,
                'meaning': str,
                'example': str,
                'example_translation': str
            }
        ]
    }
}

2. qa_pairs
{
    '_id': ObjectId,
    'transcript_id': str,
    'video_id': str,
    'video_title': str,
    'question_text': str,
    'answer': str,
    'type': str,
    'options': list[str],
    'created_at': datetime,
    'attempts': int,
    'correct_attempts': int
}

3. user_progress
{
    '_id': ObjectId,
    'user_id': str,
    'video_id': str,
    'type': str,
    'answers': dict,
    'updated_at': datetime
}

4. global_words
{
    '_id': ObjectId,
    'word': str,          # The Hindi word
    'meaning_data': {
        'meaning': str,   # English meaning
        'example': {
            'hindi': str, # Example in Hindi
            'english': str # Example in English
        }
    },
    'frequency': int,     # How many times users have queried this
    'created_at': datetime,
    'last_updated': datetime
}

5. user_words
{
    '_id': ObjectId,
    'user_id': str,      # Reference to user
    'word_id': ObjectId, # Reference to global_words
    'is_mastered': bool,
    'is_favorite': bool,
    'notes': str,        # Optional personal notes
    'created_at': datetime
}

6. curated_videos (NEW - Agentic Workflow)
{
    '_id': ObjectId,
    'video_id': str,     # YouTube video ID
    'title': str,        # Video title
    'duration': str,     # Video duration (e.g., "6:30")
    'topic': str,        # Learning topic (daily_life, family, travel, etc.)
    'difficulty': str,   # beginner, intermediate, advanced
    'metadata': {
        'key_vocabulary': [
            {
                'hindi': str,
                'english': str,
                'context': str
            }
        ],
        'grammar_patterns': [
            {
                'pattern': str,
                'examples': list[str],
                'explanation': str
            }
        ],
        'cultural_context': {
            'region': str,
            'setting': str,
            'formality': str,
            'cultural_notes': str
        },
        'learning_path': {
            'prerequisites': list[str],
            'next_steps': list[str],
            'related_videos': list[str]
        },
        'technical_specs': {
            'estimated_tokens': int,
            'chunking_strategy': str,
            'api_compatible': bool
        }
    },
    'created_at': datetime,
    'updated_at': datetime
}

7. learning_paths (NEW - Agentic Workflow)
{
    '_id': ObjectId,
    'name': str,         # Path name (e.g., "Beginner Daily Life")
    'description': str,  # Path description
    'target_level': str, # beginner, intermediate, advanced
    'topic': str,        # Primary topic focus
    'videos': [
        {
            'video_id': str,
            'order': int,
            'estimated_duration': int,  # minutes
            'learning_objectives': list[str]
        }
    ],
    'total_duration': int,  # Total estimated time in minutes
    'prerequisites': list[str],
    'learning_outcomes': list[str],
    'created_at': datetime,
    'updated_at': datetime
}

8. user_learning_progress (NEW - Agentic Workflow)
{
    '_id': ObjectId,
    'user_id': str,
    'video_id': str,
    'is_completed': bool,
    'is_favorite': bool,
    'time_spent_minutes': int,
    'average_score': float,  # 0-100
    'attempts_count': int,
    'last_watched': datetime,
    'notes': str,
    'difficulty_rating': int,  # 1-5 user rating
    'learning_path_id': str,  # Optional reference to learning path
    'created_at': datetime,
    'updated_at': datetime
}
"""