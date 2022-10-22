from django.urls import path

from user import views

urlpatterns = [
    path('test', views.test),
    path('login', views.login), # 登录
    path('register', views.register), # 注册
    
    # path("get_index_data_view", views.get_index_data),
]