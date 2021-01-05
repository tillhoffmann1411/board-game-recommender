from django.contrib import admin
from django.urls import path, include
from django.urls.conf import re_path

from rest_framework_simplejwt import views as jwt_views

urlpatterns = [
    re_path(r'^games/', include('game.urls')),
    re_path(r'^user/', include('account.urls')),

    path('signin/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh-token/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
]
