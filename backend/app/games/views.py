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
from accounts.models import UserTaste, Review
from .recommender.similiar_users import *

# The serializer alone is not able to respond to an API request, that's why we need to implement a view

# --- The manual way
# class BoardGameList(APIView):
#    permission_classes = (IsAdminOrReadOnly, IsAuthenticated,)
#     def get(self, request, format=None):
#         boardGames = BoardGame.objects.all()
#         serializer = BoardGameSerializer(boardGames, many=True)
#         return Response(serializer.data)

#     def post(self, request, format=None):
#         serializer = BoardGameSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# --- The easy way read only
# class BoardGameList(generics.ListAPIView):
#     queryset = BoardGame.objects.all()
#     serializer_class = BoardGameSerializer


# --- The easy way read and write (post and get)
class BoardGameList(generics.ListAPIView):
    # Write operations just for admins, GET for other authenticated users
    permission_classes = (IsAdminOrReadOnly, IsAuthenticated,)
    queryset = BoardGame.objects.all()
    serializer_class = BoardGameSerializer


# --- The stuff for GET PUT and DELETE

# --- The manual way
# class BoardGameDetail(APIView):
#     permission_classes = (IsAdminOrReadOnly, IsAuthenticated,)

#     def get_object(self, pk):
#         try:
#             return BoardGame.objects.get(pk=pk)
#         except BoardGame.DoesNotExist:
#             raise Http404

#     def get(self, request, pk, format=None):
#         boardGame = self.get_object(pk)
#         serializer = BoardGameSerializer(boardGame)
#         return Response(serializer.data)

#     def put(self, request, pk, format=None):
#         boardGame = self.get_object(pk)
#         serializer = BoardGameSerializer(boardGame, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def delete(self, request, pk, format=None):
#         boardGame = self.get_object(pk)
#         boardGame.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)

# --- The easy way
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

        # reviews = Review.objects.values_list('id', flat=True)       # Perform database query
        # reviews_df = read_frame(reviews)

        query = str(Review.objects.all().query)
        reviews_df = pd.read_sql_query(query, connection)

        print(str(reviews_df.head()))  #
        print('user id: ' + str(user_id))  #

        # get all data to compare
        data = get_recommendation_data(reviews_df,  # link='./app/games/recommender/Reviews.csv',
                                       min_number_ratings_game=1,
                                       min_number_ratings_user=1,
                                       size_user_sample=5_000_000,
                                       seed=2352)  # if None random games

        # create utility matrix
        data = prepare_data(data=data)

        # calculate user similarities
        result_similarity, item_requested = calculate_centered_cosine_similarity(data=data,
                                                                                 new_user=user_id)
        # create most similar user group
        data = prepare_prediction_data(data=data,
                                       item_requested=item_requested,
                                       similarities=result_similarity,
                                       threshold_compare_best_n_percentage=0.2)

        # get average game rating from similar users
        sorted_pred, pred_info = predict(data,
                                         threshold_min_number_ratings_per_game=50)

        # print('info about game predictions: \t', pred_info)

        sorted_pred = sorted_pred.to_frame().reset_index()
        # pd.DataFrame({sorted_pred.index, sorted_pred})

        return Response(sorted_pred[:50].to_dict(orient="records"))
        # return Recommendations.objects.all().filter(user=self.request.user)
