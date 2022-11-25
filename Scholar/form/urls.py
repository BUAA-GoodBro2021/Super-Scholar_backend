from django.urls import path

from form import views

urlpatterns = [
    path('user_claim_author', views.user_claim_author),  # 用户申请认领门户
    path('user_give_up_author', views.user_give_up_author),  # 用户撤销申请或者撤销认领
    path('manager_check_claim', views.manager_check_claim),  # 管理员查看未处理申请
    path("manager_deal_claim", views.manager_deal_claim),  # 管理员处理申请
    path('manager_look_all_user', views.manager_look_all_user),  # 管理员查看所有用户信息
    # path('manager_delete_user_author', views.manager_delete_user_author)  # 管理员解除用户的门户
]
