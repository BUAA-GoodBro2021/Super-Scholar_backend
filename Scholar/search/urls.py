from django.urls import path

from search import views

urlpatterns = [
    path("get_index_data_view", views.get_index_data_view),
    path("associate_content_view", views.associate_content_view),
]
