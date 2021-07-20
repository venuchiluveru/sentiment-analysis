from django.urls import path
from . import views

urlpatterns = [
    path('', views.tweet_list, name='tweet_list'),
    path('tweet_search', views.tweet_search, name='tweet_search'),
]