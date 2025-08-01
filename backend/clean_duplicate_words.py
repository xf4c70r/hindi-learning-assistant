import os
import django
import sys

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from api.services.mongo_service import mongo_service
from bson import ObjectId

def clean_duplicate_words():
    try:
        db = mongo_service.db
        print("Fetching all words from database...")
        words = list(db.global_words.find())
        seen = {}
        duplicates = []

        print("\nProcessing words...")
        # First pass: identify duplicates
        for word in words:
            normalized = word['word'].strip()
            if normalized in seen:
                duplicates.append({
                    'duplicate_id': word['_id'],
                    'original_id': seen[normalized]['_id'],
                    'word': normalized
                })
            else:
                seen[normalized] = word

        if not duplicates:
            print("\nNo duplicate words found!")
            return

        print(f"\nFound {len(duplicates)} duplicate words:")
        for dup in duplicates:
            print(f"- '{dup['word']}'")

        # Second pass: merge duplicates
        print("\nMerging duplicates...")
        for dup in duplicates:
            # Update user_words to point to the original word
            result = db.user_words.update_many(
                {'word_id': dup['duplicate_id']},
                {'$set': {'word_id': dup['original_id']}}
            )
            print(f"Updated {result.modified_count} user references for word '{dup['word']}'")

            # Delete the duplicate word
            db.global_words.delete_one({'_id': dup['duplicate_id']})
            print(f"Deleted duplicate entry for word '{dup['word']}'")

        print("\nCleanup completed successfully!")

    except Exception as e:
        print(f"\nError during cleanup: {str(e)}")

if __name__ == '__main__':
    clean_duplicate_words() 