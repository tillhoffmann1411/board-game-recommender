from django.urls import path, include
from django.urls.conf import re_path

from rest_framework_simplejwt import views as jwt_views

urlpatterns = [
    re_path(r'^games/', include('games.urls')),
    re_path(r'^user/', include('accounts.urls')),

    re_path(r'^auth/', include('dj_rest_auth.urls')),
    path('auth/register/', include('dj_rest_auth.registration.urls')),
    path('refresh-token/', jwt_views.TokenRefreshView.as_view()),
]
