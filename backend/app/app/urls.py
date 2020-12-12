from django.contrib import admin
from django.urls import path, include
from django.urls.conf import re_path

from rest_framework_jwt.views import obtain_jwt_token

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^auth/', include('rest_auth.urls')),
    re_path(r'^auth/registration/', include('rest_auth.registration.urls')),
    re_path(r'^token-auth/', obtain_jwt_token),
]
