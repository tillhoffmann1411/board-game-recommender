from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import Http404


from django.contrib.auth.models import User

from .models import Taste
from .serializers import TasteSerializer, UserSerializer
from .permissions import IsOwner, IsYourProfile


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

    def put(self, request, pk, format=None):
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


class TasteList(generics.ListCreateAPIView):
    queryset = Taste.objects.all()
    serializer_class = TasteSerializer
    permission_classes = (IsOwner, )

    def perform_create(self, serializer):
        serializer.save(
            games=self.request.data['games'],
            created_by=self.request.user),


class TasteDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TasteSerializer
    permission_classes = (IsOwner, )
    lookup_url_kwarg = 'taste_id'

    def get_queryset(self):
        taste = self.kwargs['taste_id']
        return Taste.objects.filter(id=taste)
