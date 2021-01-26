from django.conf.urls import url

from . import views

urlpatterns = [
    url('recommendation/', views.RecommendationSimiliarUsers.as_view()),
    url('recommendation/knn/', views.RecommendationKNN.as_view()),
    url(r'^(?P<pk>[0-9]+)/', views.BoardGameDetail.as_view()),
    url(r'^', views.BoardGameList.as_view()),
]
