from pandas.core import construction
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
import pandas as pd
from django.db import connection

from django_pandas.io import read_frame

from .permissions import IsAdminOrReadOnly
from .models import Author, BoardGame, Category, GameMechanic, OnlineGame, Publisher
from .serializers import AuthorSerializer, BoardGameDetailSerializer, BoardGameSerializer, CategorySerializer, MechanicSerializer, OnlineGameSerializer, PublisherSerializer

from accounts.serializers import ReviewSerializer
from accounts.models import UserTaste, Review

from .recommender.collaborative_filtering_user_based import similiar_users
from .recommender.popularity_score import popular_games
from .recommender.knn_selfmade import selfmade_KnnWithMeans_approach
from .recommender.content_based_filtering import similar_games


# View that lists all board games
class BoardGameList(generics.ListAPIView):
    # Write operations just for admins, GET for other authenticated users
    permission_classes = (IsAdminOrReadOnly, IsAuthenticated,)
    queryset = BoardGame.objects.all()
    serializer_class = BoardGameSerializer


# View that returns all details for a single board game
class BoardGameDetail(generics.RetrieveUpdateDestroyAPIView):
    # Write operations just for admins, GET for other authenticated users
    permission_classes = (IsAdminOrReadOnly, IsAuthenticated,)
    queryset = BoardGame.objects.all()
    serializer_class = BoardGameDetailSerializer


# View that that triggers and returns the results of the common based recommender
class RecommendationCommonBased(APIView):
    permission_classes = (IsAdminOrReadOnly, IsAuthenticated,)

    def get(self, *args, **kwargs):
        user_taste = generics.get_object_or_404(UserTaste, user=self.request.user)
        user_id = user_taste.id

        cursor = connection.cursor()
        cursor.execute('''
            select created_by_id, game_id, rating
            from accounts_review ar
            where created_by_id  in (
                select created_by_id
                from accounts_review
                group by created_by_id
                having count(created_by_id) >= 10
                order by random()
                limit 5000)
        ''')
        reviews = cursor.fetchall()

        reviews_df = pd.DataFrame.from_records(reviews)
        reviews_df = reviews_df.rename(columns={0: 'created_by_id', 1: 'game_key', 2: 'rating'})

        combined_reviews_df = reviews_df

        if int(user_id) not in reviews_df['created_by_id'].values:
            reviews_user_df = read_frame(Review.objects.filter(created_by=user_taste),
                                         fieldnames=['game_id__id', 'created_by__id', 'rating'])
            reviews_user_df = reviews_user_df.rename(
                columns={'created_by__id': 'created_by_id', 'game_id__id': 'game_key', 'rating': 'rating'})
            combined_reviews_df = pd.concat([reviews_df, reviews_user_df], ignore_index=True)

        return Response(similiar_users(user_id, combined_reviews_df))


# View that that triggers and returns the results of the k nearest neighbors recommender
class RecommendationKNN(APIView):
    permission_classes = (IsAdminOrReadOnly, IsAuthenticated,)

    def get(self, *args, **kwargs):
        user_taste = generics.get_object_or_404(UserTaste, user=self.request.user)

        reviews_from_user = Review.objects.all().filter(created_by=user_taste)

        reviews_from_user_df = read_frame(reviews_from_user, fieldnames=['game_id__id', 'rating'])
        reviews_from_user_df = reviews_from_user_df.rename(columns={'game_id__id': 'game_key', 'rating': 'rating'})

        return Response(selfmade_KnnWithMeans_approach(reviews_from_user_df))


# View that that triggers and returns the results of the item based recommender
class RecommendationItemBased(APIView):
    permission_classes = (IsAdminOrReadOnly, IsAuthenticated,)

    def get(self, *args, **kwargs):
        user_taste = generics.get_object_or_404(UserTaste, user=self.request.user)
        user_id = user_taste.id

        reviews_user_df = read_frame(Review.objects.filter(created_by=user_taste),
                                     fieldnames=['game_id__id', 'created_by__id', 'rating'])
        reviews_user_df = reviews_user_df.rename(
            columns={'created_by__id': 'user_key', 'game_id__id': 'game_key', 'rating': 'rating'})

        return Response(similar_games(user_id, reviews_user_df))


# View that that triggers and returns the results of the popularity recommender
class RecommendationPopularity(APIView):
    permission_classes = (IsAdminOrReadOnly, IsAuthenticated,)

    def get(self, *args, **kwargs):
        boardgames_df = read_frame(BoardGame.objects.all(), fieldnames=[
                                   'id', 'name', 'bgg_num_ratings', 'bga_num_ratings', 'bgg_avg_rating'])
        boardgames_df = boardgames_df.rename(columns={'id': 'game_key', 'bgg_num_ratings': 'bgg_num_user_ratings',
                                                      'bga_num_ratings': 'bga_num_user_ratings', 'bgg_avg_rating': 'bgg_average_user_rating'})

        return Response(popular_games(boardgames_df))


# View that that returns all categories
class CategoryList(generics.ListAPIView):
    permission_classes = (IsAdminOrReadOnly, IsAuthenticated,)
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


# View that that returns all mechanics
class MechanicList(generics.ListAPIView):
    permission_classes = (IsAdminOrReadOnly, IsAuthenticated,)
    queryset = GameMechanic.objects.all()
    serializer_class = MechanicSerializer


# View that that returns all authors
class AuthorList(generics.ListAPIView):
    permission_classes = (IsAdminOrReadOnly, IsAuthenticated,)
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer


# View that that returns all publishers
class PublisherList(generics.ListAPIView):
    permission_classes = (IsAdminOrReadOnly, IsAuthenticated,)
    queryset = Publisher.objects.all()
    serializer_class = PublisherSerializer


# View that that returns all online games for a given board game
class OnlineGameDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OnlineGameSerializer
    queryset = OnlineGame.objects.all()
    permission_classes = (IsAdminOrReadOnly, IsAuthenticated,)
    lookup_field = 'bgg_id'
