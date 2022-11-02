from django.urls import path
from follow import views

urlpatterns = [
    path('follow_author', views.follow_author),
    path('unfollow_author', views.unfollow_author),
    path('follow_list', views.follow_list),
]