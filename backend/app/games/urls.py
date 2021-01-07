from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^(?P<pk>[0-9]+)/$', views.BoardGameDetail.as_view()),
    url(r'^', views.BoardGameList.as_view()),
]
