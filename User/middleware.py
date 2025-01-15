from django.utils.deprecation import MiddlewareMixin
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

User = get_user_model()

class TokenAuthenticationMiddleware(MiddlewareMixin):
    """
    Middleware to authenticate user based on access token in request headers.
    """

    def process_request(self, request):
        # Check for the Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION')

        if auth_header is None:
            return None  # No token provided, proceed with the request

        # Split the header into parts
        try:
            prefix, token = auth_header.split()
            if prefix.lower() != 'bearer':
                raise AuthenticationFailed('Authorization header must start with Bearer')
        except ValueError:
            raise AuthenticationFailed('Invalid Authorization header format')

        try:
            # Decode the access token
            validated_token = AccessToken(token)
            user_id = validated_token['user_id']  # Get user_id from the token
            
            # Get the user corresponding to the user_id
            request.user = User.objects.get(id=user_id)  # Set the user object in the request
        except (AuthenticationFailed, User.DoesNotExist) as e:
            raise AuthenticationFailed('Invalid token or user does not exist')

        return None  # Proceed with the request