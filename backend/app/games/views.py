from pandas.core import construction
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
import pandas as pd
from django.db import connection

from django_pandas.io import read_frame

from .permissions import IsAdminOrReadOnly
from .models import BoardGame, Recommendations
from .serializers import BoardGameDetailSerializer, BoardGameSerializer, RecommendationSerializer
from accounts.serializers import ReviewSerializer
from accounts.models import UserTaste, Review

from .recommender.similiar_users import similiar_users
from .recommender.knn_with_means_selfmade import selfmade_KnnWithMeans_approach


class BoardGameList(generics.ListAPIView):
    # Write operations just for admins, GET for other authenticated users
    permission_classes = (IsAdminOrReadOnly, IsAuthenticated,)
    queryset = BoardGame.objects.all()
    serializer_class = BoardGameSerializer


class BoardGameDetail(generics.RetrieveUpdateDestroyAPIView):
    # Write operations just for admins, GET for other authenticated users
    permission_classes = (IsAdminOrReadOnly, IsAuthenticated,)
    queryset = BoardGame.objects.all()
    serializer_class = BoardGameDetailSerializer


class RecommendationSimiliarUsers(APIView):
    permission_classes = (IsAdminOrReadOnly, IsAuthenticated,)

    def get(self, *args, **kwargs):
        user_taste = generics.get_object_or_404(UserTaste, user=self.request.user)
        user_id = user_taste.id

        reviews_df = read_frame(Review.objects.all(), fieldnames=['game_id__id', 'rating', 'created_by_id__id'])
        reviews_df = reviews_df.rename(columns={'game_id__id': 'game_key',
                                                'rating': 'rating', 'created_by_id__id': 'created_by_id'})

        return Response(similiar_users(user_id, reviews_df))


class RecommendationKNN(APIView):
    permission_classes = (IsAdminOrReadOnly, IsAuthenticated,)

    def get(self, *args, **kwargs):
        user_taste = generics.get_object_or_404(UserTaste, user=self.request.user)
        user_id = user_taste.id

        reviews_from_user = Review.objects.all().filter(created_by=user_taste)

        reviews_from_user_df = read_frame(reviews_from_user, fieldnames=['game_id__id', 'rating'])
        reviews_from_user_df = reviews_from_user_df.rename(columns={'game_id__id': 'game_key', 'rating': 'rating'})

        print(str(reviews_from_user_df.head()))

        return Response(selfmade_KnnWithMeans_approach(user_id, reviews_from_user_df))


class RecommendationItemBased(APIView):
    permission_classes = (IsAdminOrReadOnly, IsAuthenticated,)

    def get(self, *args, **kwargs):

        return Response([{'game_key': 100001, 'estimate': 9.999}, ])
