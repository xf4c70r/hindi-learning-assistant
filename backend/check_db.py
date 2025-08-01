import os
import django
import sys

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from api.services.mongo_service import mongo_service
from bson import ObjectId

def check_words():
    try:
        db = mongo_service.db
        print("\nFetching all words from database...")
        words = list(db.global_words.find())
        
        print("\nAll words in database:")
        for word in words:
            print(f"ID: {word['_id']}, Word: \"{word['word']}\", Frequency: {word.get('frequency', 1)}")
            
        print("\nTotal words:", len(words))
        
        # Ask user if they want to delete any words
        print("\nWould you like to delete any words? Enter the ID to delete, or 'q' to quit:")
        while True:
            word_id = input("> ")
            if word_id.lower() == 'q':
                break
                
            try:
                result = db.global_words.delete_one({'_id': ObjectId(word_id)})
                if result.deleted_count > 0:
                    print(f"Successfully deleted word with ID: {word_id}")
                else:
                    print(f"No word found with ID: {word_id}")
            except Exception as e:
                print(f"Error deleting word: {str(e)}")

    except Exception as e:
        print(f"\nError: {str(e)}")

if __name__ == '__main__':
    check_words()
