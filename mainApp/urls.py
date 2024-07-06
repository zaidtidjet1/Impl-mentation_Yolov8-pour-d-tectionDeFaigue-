from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [

    path('', views.index,name="index"),
    path('video-feed-live', views.video_feed_live,name="video-feed-live"),
    path('video-feed', views.video_feed,name="video-feed"),
    path('stop_streaming', views.stop_streaming,name="stop_streaming"),
]
