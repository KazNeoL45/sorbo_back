import base64
import json
import time
from django.contrib.auth.models import User
from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed


class SimpleTokenAuthentication(authentication.BaseAuthentication):
    """
    Custom authentication that works with our simple base64-encoded tokens.
    """
    
    def authenticate(self, request):
        """
        Returns a two-tuple of `User` and token if authentication is successful.
        Otherwise, returns None if the token is invalid, expired, or not provided.
        """
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        try:
            # Decode the base64 token
            token_data = base64.b64decode(raw_token).decode('utf-8')
            token_payload = json.loads(token_data)
            
            # Check if token is expired
            if 'exp' in token_payload:
                if time.time() > token_payload['exp']:
                    return None  # Token expired
            
            # Get user from token
            user_id = token_payload.get('user_id')
            if user_id:
                try:
                    user = User.objects.get(id=user_id)
                    return (user, token_payload)
                except User.DoesNotExist:
                    return None
            
            return None
            
        except (base64.binascii.Error, json.JSONDecodeError, KeyError, ValueError):
            # Invalid token format
            return None
    
    def get_header(self, request):
        """
        Extract the authorization header from the request.
        """
        header = request.META.get('HTTP_AUTHORIZATION')
        if isinstance(header, str):
            header = header.encode('iso-8859-1')
        return header
    
    def get_raw_token(self, header):
        """
        Extract the raw token from the authorization header.
        """
        parts = header.decode().split()
        
        if len(parts) == 0:
            return None
            
        if parts[0].lower() != 'bearer':
            return None
            
        if len(parts) != 2:
            return None
            
        return parts[1]
