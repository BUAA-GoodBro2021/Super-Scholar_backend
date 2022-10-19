from django.urls import path

from utils import views

urlpatterns = [
    path("clear_redis_all", views.clear_redis_all),
]