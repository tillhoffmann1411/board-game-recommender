from rest_framework.permissions import BasePermission, SAFE_METHODS

from .models import UserTaste


class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.created_by == request.user


class IsYourReview(BasePermission):
    def is_your_review(self, request, view, obj):
        user_taste = UserTaste.objects.get(user=self.request.user)
        return obj.created_by == user_taste


class IsYourProfile(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.id == request.user.id
