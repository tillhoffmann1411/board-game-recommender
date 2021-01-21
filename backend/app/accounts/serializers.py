from rest_framework import serializers
from django.http import JsonResponse

from django.contrib.auth.models import User

from games.serializers import BoardGameSerializer

from .models import Review, UserTaste


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')


class UserTasteSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = UserTaste
        fields = ('id', 'username', 'number_of_ratings', 'user')


class ReviewSerializer(serializers.ModelSerializer):
    # This is required to accept only game ids to update
    game = serializers.PrimaryKeyRelatedField(many=False, read_only=True)
    created_by = serializers.PrimaryKeyRelatedField(many=False, read_only=True)

    class Meta:
        model = Review
        fields = ('id', 'rating', 'created_at', 'created_by', 'game')
        read_only_fields = ['created_by', 'game']
        depth = 0
        extra_kwargs = {
            'created_by': {'write_only': True}
        }

    def create(self, validated_data):
        review, created = Review.objects.update_or_create(
            game=validated_data.get('game', None),
            created_by=validated_data.get('created_by', None),
            defaults={'rating': validated_data.get('rating', None)})
        return review
