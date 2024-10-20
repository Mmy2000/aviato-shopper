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
