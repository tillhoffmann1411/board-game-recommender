from rest_framework import serializers
from django.http import JsonResponse

from django.contrib.auth.models import User
from game.serializers import BoardGameSerializer
from game.models import BoardGame

from .models import Taste


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')


class TasteSerializer(serializers.ModelSerializer):
    # This is required to accept only game ids to update
    games = serializers.PrimaryKeyRelatedField(
        many=True, read_only=False, queryset=BoardGame.objects.all())
    # When Serializing the Database Object just return the username
    created_by = serializers.ReadOnlyField(source='created_by.username')

    class Meta:
        model = Taste
        fields = ('id', 'games', 'created_by', 'created_at', 'updated_at')
