from rest_framework import permissions

class IsSuperAdmin(permissions.BasePermission):
    """
    Custom permission to allow only super admins to add, update, or delete products.
    """

    message = "Only super admins are allowed to perform this action."

    def has_permission(self, request, view):
        # Allow read-only methods for everyone
        if request.method in permissions.SAFE_METHODS:
            return True
        # Restrict write methods to super admin users only
        return request.user.is_authenticated and request.user.is_superadmin

class IsOwnerOrSuperuser(permissions.BasePermission):
    """
    Custom permission to only allow owners of a review or superusers to delete it.
    """
    def has_object_permission(self, request, view, obj):
        # Allow delete if the user is the owner of the review or is a superuser
        return obj.user == request.user or request.user.is_superadmin
    
class IsSuperUserOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow superusers to create, update, or delete objects.
    """
    def has_permission(self, request, view):
        # Allow listing without authentication
        if view.action == 'list':
            return True
        
        # Allow create, update, or delete for superusers only
        return request.user and request.user.is_superadmin

    def has_object_permission(self, request, view, obj):
        # Allow safe methods (GET, HEAD, OPTIONS) or superuser actions
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user and request.user.is_superadmin