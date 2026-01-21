from django.http import Http404

from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from django.contrib.auth.models import User
from games.models import BoardGame

from .models import Review, UserTaste
from .serializers import ReviewSerializer, UserSerializer
from .permissions import IsYourReview


# View for read, write and delete operations on an user
class UserDetail(APIView):
    permission_classes = (IsAuthenticated, )

    def get_object(self):
        try:
            return User.objects.get(pk=self.request.user.id)
        except User.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        user = self.request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def put(self, request, format=None):
        user = self.request.user
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        user = self.request.user
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# View for read and write operations
class ReviewList(generics.ListCreateAPIView):
    queryset = Review.objects.all().select_related('rating', 'game_id', 'created_at')
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthenticated, IsYourReview)

    def perform_create(self, serializer):
        user_taste = UserTaste.objects.get(user=self.request.user)
        serializer.save(
            game=BoardGame.objects.get(id=self.request.data['game']),
            created_by=user_taste,
            rating=self.request.data['rating']),

    def get_queryset(self, *args, **kwargs):
        user_taste = generics.get_object_or_404(UserTaste, user=self.request.user)
        return Review.objects.all().filter(created_by=user_taste)


# View mainly for deleting a single rating
class ReviewDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthenticated, IsYourReview)
    queryset = Review.objects.all()
