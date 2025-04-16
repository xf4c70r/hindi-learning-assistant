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
                'is_active': True
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
        # Add user_id to request if authenticated
        if hasattr(request, 'user') and request.user.is_authenticated:
            request.user_id = request.user.id
        return self.get_response(request) 