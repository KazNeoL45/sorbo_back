from rest_framework import permissions


class IsAuthenticatedOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow read-only access for unauthenticated users
    and full access for authenticated users.
    """
    
    def has_permission(self, request, view):
        # Allow read-only access for unauthenticated users
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Require authentication for write operations
        return request.user and request.user.is_authenticated


class IsAdminUser(permissions.BasePermission):
    """
    Custom permission to allow access only to admin users.
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_staff
