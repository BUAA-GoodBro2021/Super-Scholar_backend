from django.urls import path

from comment import views

urlpatterns = [
    path('add_comment', views.add_comment),
]