from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^review/(?P<pk>[0-9]+)/', views.ReviewDetail.as_view()),
    url(r'^review/', views.ReviewList.as_view()),

    url(r'^', views.UserDetail.as_view()),
    # url(r'^', views.UserList.as_view()),

]
