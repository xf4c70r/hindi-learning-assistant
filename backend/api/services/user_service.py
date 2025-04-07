from datetime import datetime
from bson import ObjectId
from django.contrib.auth.hashers import make_password, check_password
from .mongo_service import mongo_service

class UserService:
    def __init__(self):
        self.db = mongo_service.db
        self._ensure_indexes()

    def _ensure_indexes(self):
        """Create necessary indexes for the users collection"""
        self.db.users.create_index('email', unique=True)
        self.db.users.create_index('username', unique=True)

    def create_user(self, email, password, first_name='', last_name=''):
        """Create a new user in MongoDB"""
        try:
            # Hash the password
            hashed_password = make_password(password)
            
            # Create user document
            user_doc = {
                'email': email,
                'username': email,  # Using email as username
                'password': hashed_password,
                'first_name': first_name,
                'last_name': last_name,
                'is_active': True,
                'date_joined': datetime.utcnow(),
                'last_login': None
            }
            
            # Insert into MongoDB
            result = self.db.users.insert_one(user_doc)
            
            # Get the created user
            user = self.db.users.find_one({'_id': result.inserted_id})
            user['id'] = str(user['_id'])  # Add id field for JWT
            
            return user
            
        except Exception as e:
            raise Exception(f"Error creating user: {str(e)}")

    def get_user_by_email(self, email):
        """Get user by email"""
        user = self.db.users.find_one({'email': email})
        if user:
            user['id'] = str(user['_id'])  # Add id field for JWT
        return user

    def verify_password(self, user, password):
        """Verify user's password"""
        return check_password(password, user['password'])

    def update_last_login(self, user_id):
        """Update user's last login time"""
        self.db.users.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'last_login': datetime.utcnow()}}
        )

    def user_exists(self, email):
        """Check if a user with the given email exists"""
        return self.db.users.count_documents({'email': email}) > 0

# Create singleton instance
user_service = UserService() 