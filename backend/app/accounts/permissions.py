from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.created_by == request.user


class IsYourProfile(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.id == request.user.id
