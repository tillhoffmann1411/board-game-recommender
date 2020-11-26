from django.conf.urls import url
from QuestionaireApp import views

urlpatterns = [
    url(r'^questionaire/$', views.qustionaireApi)
]
