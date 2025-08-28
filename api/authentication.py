from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


class OptionalJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication that doesn't fail for public endpoints when an invalid token is provided.
    This allows public endpoints to work even when an expired/invalid token is sent in the Authorization header.
    """
    
    def authenticate(self, request):
        """
        Returns a two-tuple of `User` and token if authentication is successful.
        Otherwise, returns None if the token is invalid, expired, or not provided.
        This allows views to handle authentication optionally based on their permission classes.
    """
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        try:
            validated_token = self.get_validated_token(raw_token)
            return self.get_user(validated_token), validated_token
        except (InvalidToken, TokenError):
            # Return None instead of raising an exception
            # This allows the view's permission classes to decide whether auth is required
            return None
