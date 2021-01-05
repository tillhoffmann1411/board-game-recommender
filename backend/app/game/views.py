from django.http import Http404

from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


from .permissions import IsAdminOrReadOnly
from .models import BoardGame
from .serializers import BoardGameSerializer

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
class BoardGameList(generics.ListCreateAPIView):
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
    serializer_class = BoardGameSerializer
