import os
import sys
import django
from datetime import datetime

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.contrib.auth.models import User
from api.services.user_service import user_service
from api.services.mongo_service import mongo_service

def migrate_users():
    """Migrate users from SQLite to MongoDB"""
    print("\n=== Starting User Migration to MongoDB ===\n")
    
    # Get total count for progress tracking
    total_users = User.objects.count()
    print(f"Found {total_users} users to migrate")
    
    # Create indexes
    mongo_service.db.users.create_index('email', unique=True)
    mongo_service.db.users.create_index('username', unique=True)
    
    # Track migration progress
    successful_migrations = 0
    failed_migrations = []
    
    # Migrate each user
    for user in User.objects.all():
        print(f"\nMigrating user: {user.email}")
        
        try:
            # Check if user already exists in MongoDB
            if user_service.user_exists(user.email):
                print(f"✓ User {user.email} already exists in MongoDB")
                successful_migrations += 1
                continue
            
            # Create user document
            user_doc = {
                'email': user.email,
                'username': user.username,
                'password': user.password,  # Already hashed by Django
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_active': user.is_active,
                'date_joined': user.date_joined,
                'last_login': user.last_login
            }
            
            # Insert into MongoDB
            result = mongo_service.db.users.insert_one(user_doc)
            print(f"✓ Successfully migrated user: {user.email}")
            successful_migrations += 1
            
        except Exception as e:
            print(f"✗ Error migrating user {user.email}: {str(e)}")
            failed_migrations.append({
                'email': user.email,
                'error': str(e)
            })
    
    # Print summary
    print("\n=== Migration Summary ===")
    print(f"Total users: {total_users}")
    print(f"Successfully migrated: {successful_migrations}")
    print(f"Failed migrations: {len(failed_migrations)}")
    
    if failed_migrations:
        print("\nFailed migrations details:")
        for failure in failed_migrations:
            print(f"- {failure['email']}: {failure['error']}")
    
    if successful_migrations == total_users:
        print("\n✅ Migration completed successfully!")
    else:
        print("\n⚠️ Migration completed with some issues. Please check the logs above.")

if __name__ == "__main__":
    # Ask for confirmation before proceeding
    response = input("This will migrate users to MongoDB. The existing SQLite data will be preserved. Proceed? (y/n): ")
    if response.lower() == 'y':
        migrate_users()
    else:
        print("Migration cancelled.") 