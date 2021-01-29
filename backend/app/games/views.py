from pandas.core import construction
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
import pandas as pd
from django.db import connection

from django_pandas.io import read_frame

from .permissions import IsAdminOrReadOnly
from .models import Author, BoardGame, Category, GameMechanic, OnlineGame, Publisher, Recommendations
from .serializers import AuthorSerializer, BoardGameDetailSerializer, BoardGameSerializer, CategorySerializer, MechanicSerializer, OnlineGameSerializer, PublisherSerializer, RecommendationSerializer
from accounts.serializers import ReviewSerializer
from accounts.models import UserTaste, Review

from .recommender.similar_users import similiar_users
# from .recommender.similar_users import similiar_items
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


class RecommendationCommonBased(APIView):
    permission_classes = (IsAdminOrReadOnly, IsAuthenticated,)

    def get(self, *args, **kwargs):
        user_taste = generics.get_object_or_404(UserTaste, user=self.request.user)
        user_id = user_taste.id

        reviews_df = read_frame(Review.objects.all(), fieldnames=['game_id__id', 'rating', 'created_by_id__id'])
        reviews_df = reviews_df.rename(columns={'game_id__id': 'game_key', 'created_by_id__id': 'created_by_id'})

        print(str(reviews_df.head()))
        return Response(similiar_users(user_id, reviews_df))


class RecommendationKNN(APIView):
    permission_classes = (IsAdminOrReadOnly, IsAuthenticated,)

    def get(self, *args, **kwargs):
        user_taste = generics.get_object_or_404(UserTaste, user=self.request.user)
        user_id = user_taste.id

        reviews_from_user = Review.objects.all().filter(created_by=user_taste)

        reviews_from_user_df = read_frame(reviews_from_user, fieldnames=['game_id__id', 'rating'])
        reviews_from_user_df = reviews_from_user_df.rename(columns={'game_id__id': 'game_key', 'rating': 'rating'})

        return Response(selfmade_KnnWithMeans_approach(user_id, reviews_from_user_df))


class RecommendationItemBased(APIView):
    permission_classes = (IsAdminOrReadOnly, IsAuthenticated,)

    def get(self, *args, **kwargs):
        # Call here similiar items function

        return Response([{'game_key': 100001, 'estimate': 9.999}, ])


class RecommendationPopularity(APIView):
    permission_classes = (IsAdminOrReadOnly, IsAuthenticated,)

    def get(self, *args, **kwargs):
        # Call here similiar items function

        return Response([{'game_key': 100001, 'estimate': 9.999}, ])


class CategoryList(generics.ListAPIView):
    permission_classes = (IsAdminOrReadOnly, IsAuthenticated,)
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class MechanicList(generics.ListAPIView):
    permission_classes = (IsAdminOrReadOnly, IsAuthenticated,)
    queryset = GameMechanic.objects.all()
    serializer_class = MechanicSerializer


class AuthorList(generics.ListAPIView):
    permission_classes = (IsAdminOrReadOnly, IsAuthenticated,)
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer


class PublisherList(generics.ListAPIView):
    permission_classes = (IsAdminOrReadOnly, IsAuthenticated,)
    queryset = Publisher.objects.all()
    serializer_class = PublisherSerializer


class OnlineGameDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OnlineGameSerializer
    queryset = OnlineGame.objects.all()
    permission_classes = (IsAdminOrReadOnly, IsAuthenticated,)
    lookup_field = 'bgg_id'
