from django.urls import path
from . import views
from . import auth_views as custom_auth_views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', custom_auth_views.custom_login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('profile/<str:username>/followers/', views.followers_list, name='followers_list'),
    path('profile/<str:username>/following/', views.following_list, name='following_list'),
    path('follow/<str:username>/', views.follow_toggle, name='follow_toggle'),
    path('like/<int:tweet_id>/', views.like_tweet, name='like_tweet'),
    path('tweet/<int:tweet_id>/', views.tweet_detail, name='tweet_detail'),
    path('retweet/<int:tweet_id>/', views.retweet, name='retweet'),
    path('share/<int:tweet_id>/', views.share_tweet, name='share_tweet'),
    path('notifications/', views.notifications, name='notifications'),
    path('messages/', views.inbox, name='inbox'),
    path('messages/<str:username>/', views.conversation, name='conversation'),
    path('explore/', views.explore, name='explore'),
]
