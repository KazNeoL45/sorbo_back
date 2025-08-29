from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin


class CORSMiddleware(MiddlewareMixin):
    """
    Custom CORS middleware to handle OPTIONS requests explicitly
    """
    
    def process_request(self, request):
        # Handle preflight OPTIONS requests
        if request.method == 'OPTIONS':
            response = HttpResponse()
            response["Access-Control-Allow-Origin"] = "*"
            response["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            response["Access-Control-Allow-Headers"] = "Content-Type, Authorization, Accept, Origin"
            response["Access-Control-Max-Age"] = "86400"
            return response
        return None
    
    def process_response(self, request, response):
        # Add CORS headers to all responses
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, Authorization, Accept, Origin"
        return response
