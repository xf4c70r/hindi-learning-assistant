import os
import sys
from pymongo import MongoClient
from dotenv import load_dotenv
import certifi
from urllib.parse import quote_plus

# Set up environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv()

def migrate_to_atlas():
    """Migrate data from local MongoDB to MongoDB Atlas"""
    local_client = None
    atlas_client = None
    
    try:
        # Connect to local MongoDB
        local_client = MongoClient('localhost', 27017)
        local_db = local_client['hindi_qa_db']

        # Connect to MongoDB Atlas
        uri = os.getenv('MONGODB_URI')
        if not uri:
            raise ValueError("MONGODB_URI environment variable is not set")

        # Handle URL encoding of username and password if needed
        if '<' in uri and '>' in uri:
            # Extract and encode password
            start = uri.find(':<') + 2
            end = uri.find('>', start)
            if start > 1 and end > start:
                password = uri[start:end]
                encoded_password = quote_plus(password)
                uri = uri.replace(f'<{password}>', encoded_password)

        atlas_client = MongoClient(uri, tlsCAFile=certifi.where())
        atlas_db = atlas_client['hindi_qa_db']

        # Collections to migrate
        collections = ['transcripts', 'qa_pairs', 'youtube_videos', 'user_progress']

        for collection_name in collections:
            print(f"\nMigrating collection: {collection_name}")
            
            # Get documents from local
            local_docs = list(local_db[collection_name].find({}))
            if not local_docs:
                print(f"No documents found in local {collection_name}")
                continue

            print(f"Found {len(local_docs)} documents to migrate")

            # Insert into Atlas
            if len(local_docs) > 0:
                atlas_db[collection_name].insert_many(local_docs)
                print(f"✅ Successfully migrated {len(local_docs)} documents")

        print("\n✅ Migration completed successfully!")

    except Exception as e:
        print(f"\n❌ Error during migration: {str(e)}")
    finally:
        if local_client:
            local_client.close()
        if atlas_client:
            atlas_client.close()

if __name__ == "__main__":
    response = input("This will migrate your local MongoDB data to Atlas. Proceed? (y/n): ")
    if response.lower() == 'y':
        migrate_to_atlas()
    else:
        print("Migration cancelled.") 