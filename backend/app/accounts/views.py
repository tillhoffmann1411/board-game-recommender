from rest_framework.permissions import IsAuthenticated
from rest_framework import generics

from django.contrib.auth.models import User

from .models import Taste
from .serializers import TasteSerializer, UserSerializer
from .permissions import IsOwner


class UserList(generics.ListCreateAPIView):
    # Write operations just for admins, GET for other authenticated users
    permission_classes = (IsAuthenticated,)
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    # Write operations just for admins, GET for other authenticated users
    permission_classes = (IsAuthenticated,)
    queryset = User.objects.all()
    serializer_class = UserSerializer


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
