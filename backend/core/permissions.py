from rest_framework import permissions

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or admins to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the snippet or admin.
        if request.user and request.user.is_staff:
            return True

        # Check if obj is the user itself (for Profile model)
        if hasattr(obj, 'email') and hasattr(obj, 'is_staff'): # Simple duck typing for Profile/User object
             return obj == request.user

        # Check if obj has a 'profile' attribute (for Question, Answer models)
        if hasattr(obj, 'profile'):
            return obj.profile == request.user
            
        return False

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff
