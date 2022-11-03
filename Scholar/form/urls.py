from django.urls import path

from form import views

urlpatterns = [
    path('user_claim_author', views.user_claim_author),  # 用户申请认领门户

    # path("get_index_data_view", views.get_index_data),
]
