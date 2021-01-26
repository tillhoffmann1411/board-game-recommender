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


class Recommendation(APIView):
    # serializer_class = RecommendationSerializer
    # queryset = Recommendations.objects.all()
    permission_classes = (IsAdminOrReadOnly, IsAuthenticated,)

    def get(self, *args, **kwargs):
        user_taste = UserTaste.objects.get(user=self.request.user)
        user_id = user_taste.id

        reviews_df = read_frame(Review.objects.all(), fieldnames=['game_id__id', 'rating', 'created_by_id__id'])
        reviews_df = reviews_df.rename(columns={'game_id__id': 'game_id',
                                                'rating': 'rating', 'created_by_id__id': 'created_by_id'})

        print('Data Usage: ' + str(reviews_df.memory_usage(index=True).sum()))

        return Response(similiar_users(user_id, reviews_df))
