from django.urls import path

from message import views

urlpatterns = [
    path('look_message_list', views.look_message_list),
    path('delete_message', views.delete_message),
    path('look_unread_message_count',views.look_unread_message_count),
    path('message_test_send', views.message_test_send)
    # path("get_index_data_view", views.get_index_data),
]
