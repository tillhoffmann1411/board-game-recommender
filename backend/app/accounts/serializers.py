from rest_framework import serializers
from django.http import JsonResponse

from django.contrib.auth.models import User

from games.models import BoardGame

from .models import Review, UserTaste


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')


class ReviewSerializer(serializers.ModelSerializer):
    # This is required to accept only game ids to update
    games = serializers.PrimaryKeyRelatedField(read_only=False, queryset=BoardGame.objects.all())
    # When Serializing the Database Object just return the username
    created_by = serializers.ReadOnlyField(source='created_by')

    class Meta:
        model = Review
        fields = ('id', 'game', 'user', 'rating', 'text', 'created_at')


class UserTasteSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = UserTaste
        fields = ('id', 'username', 'number_of_reviews', 'user')
