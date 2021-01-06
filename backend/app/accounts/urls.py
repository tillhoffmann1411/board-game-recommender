from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^taste/(?P<pk>[0-9]+)/', views.TasteDetail.as_view()),
    url(r'^taste/', views.TasteList.as_view()),

    url(r'^', views.UserDetail.as_view()),
    # url(r'^', views.UserList.as_view()),

]
