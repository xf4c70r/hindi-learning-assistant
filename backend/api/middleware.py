from django.utils.functional import SimpleLazyObject
from rest_framework_simplejwt.authentication import JWTAuthentication
from .services.user_service import user_service

class MongoUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get JWT token from request
        jwt_auth = JWTAuthentication()
        try:
            validated_token = jwt_auth.get_validated_token(request.headers.get('Authorization', '').split(' ')[1])
            user_id = validated_token['user_id']
            # Add MongoDB user ID to request
            request.user_id = user_id
        except Exception:
            # If token is invalid or not present, user_id will be None
            request.user_id = None

        response = self.get_response(request)
        return response 