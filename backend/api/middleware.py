from django.utils.functional import SimpleLazyObject
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import AnonymousUser
from bson import ObjectId
from .services.user_service import user_service

class MongoJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        """
        Overridden to handle MongoDB ObjectId user IDs
        """
        try:
            user_id = validated_token['user_id']
            if user_id is None:
                return None
            
            # Create a simple user object with the MongoDB ID
            user = type('MongoUser', (), {
                'id': user_id,
                'is_authenticated': True,
                'is_active': True,
                'user_id': user_id  # Add user_id as a property of the user object
            })()
            
            return user
        except KeyError:
            raise AuthenticationFailed('No user ID in token')
        except Exception as e:
            raise AuthenticationFailed(str(e))

class MongoUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Initialize user_id as None
        request.user_id = None
        
        # Try to get the JWT token from the Authorization header
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            try:
                # Extract and validate the token
                jwt_auth = MongoJWTAuthentication()
                token = auth_header.split(' ')[1]
                validated_token = jwt_auth.get_validated_token(token)
                
                # Set user_id from the token
                request.user_id = validated_token.get('user_id')
            except Exception as e:
                # Log the error but continue processing the request
                print(f"Error processing JWT token: {str(e)}")
                pass
        
        response = self.get_response(request)
        return response 