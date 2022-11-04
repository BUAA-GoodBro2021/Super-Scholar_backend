from django.urls import path

from form import views

urlpatterns = [
    path('user_claim_author', views.user_claim_author),  # 用户申请认领门户
    path('manager_check_claim', views.manager_check_claim),  # 管理员查看未处理申请
    # path("get_index_data_view", views.get_index_data),
]
