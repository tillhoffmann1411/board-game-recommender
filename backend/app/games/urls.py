from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^online-game/(?P<bgg_id>[0-9]+)/', views.OnlineGameDetail.as_view()),
    url('recommendation/knn/', views.RecommendationKNN.as_view()),
    url('recommendation/item-based/', views.RecommendationItemBased.as_view()),
    url('recommendation/common-based/', views.RecommendationCommonBased.as_view()),
    url('recommendation/popularity/', views.RecommendationPopularity.as_view()),

    url('category/', views.CategoryList.as_view()),
    url('mechanic/', views.MechanicList.as_view()),
    url('author/', views.AuthorList.as_view()),
    url('publisher/', views.PublisherList.as_view()),


    url(r'^(?P<pk>[0-9]+)/', views.BoardGameDetail.as_view()),
    url(r'^', views.BoardGameList.as_view()),
]
