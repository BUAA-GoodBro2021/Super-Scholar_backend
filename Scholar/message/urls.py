from django.urls import path

from message import views

urlpatterns = [
    path('look_message_list', views.look_message_list),
    path('delete_message', views.delete_message),
    # path("get_index_data_view", views.get_index_data),
]
