from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='anime_index'),
    path('css/', views.stylesheet, name='stylesheet_css'),
    path('recommendation/<int:pk>/', views.recommendation, name='recommendation'),
    path('my-anime/', views.anime_list, name='my_anime'),
    path('my-friends/', views.friend_list, name='my_friends'),
    path('my-anime/<str:anime>', views.anime_unwatch, name='anime-unwatch'),
    path('my-anime/watch/<str:anime>', views.anime_watch, name='anime-watch'),
    path('my-friends/<str:friend>', views.unfriend, name='unfriend'),
    path('my-friends/watch/<str:friend>', views.befriend, name='befriend'),
]