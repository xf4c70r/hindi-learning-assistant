from api.services.mongo_service import mongo_service
from datetime import datetime

def test_mongo_connection():
    try:
        # Test connection
        db = mongo_service.db
        print("Successfully connected to MongoDB")
        
        # Clear existing test data
        db.qa_pairs.delete_many({'is_test': True})
        db.user_progress.delete_many({'is_test': True})
        
        # Insert test practice set
        test_questions = [
            {
                'video_id': 'test123',
                'video_title': 'Test Hindi Video',
                'question_text': 'What is this test about?',
                'answer': 'This test is about Hindi QA',
                'type': 'novice',
                'created_at': datetime.utcnow(),
                'attempts': 0,
                'correct_attempts': 0,
                'is_test': True
            },
            {
                'video_id': 'test123',
                'video_title': 'Test Hindi Video',
                'question_text': 'Choose the correct option:',
                'answer': 'B',
                'type': 'mcq',
                'options': ['A', 'B', 'C', 'D'],
                'created_at': datetime.utcnow(),
                'attempts': 0,
                'correct_attempts': 0,
                'is_test': True
            }
        ]
        
        result = db.qa_pairs.insert_many(test_questions)
        print(f"Inserted {len(result.inserted_ids)} test questions")
        
        # Verify data
        practice_sets = list(db.qa_pairs.aggregate([
            {
                '$group': {
                    '_id': {
                        'video_id': '$video_id',
                        'type': '$type'
                    },
                    'questionCount': {'$sum': 1},
                    'title': {'$first': '$video_title'},
                    'created_at': {'$first': '$created_at'}
                }
            }
        ]))
        
        print("\nAvailable practice sets:")
        for ps in practice_sets:
            print(f"Video: {ps['title']}, Type: {ps['_id']['type']}, Questions: {ps['questionCount']}")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_mongo_connection() 