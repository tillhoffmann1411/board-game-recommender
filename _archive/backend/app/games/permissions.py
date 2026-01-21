from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):
  # Only allow admins to perform write requests
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:  # SAFE_METHODS are GET, HEAD and OPTIONS
            return True
        else:
            return request.user.is_staff
