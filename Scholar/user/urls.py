from django.urls import path

from user import views

urlpatterns = [
    path('test', views.test),
    path('login', views.login),  # 登录
    path('register', views.register),  # 注册
    path('find_password', views.find_password),  # 找回密码，重置密码
    path('edit_introduction', views.edit_introduction),
    path('get_user', views.get_user),  # 返回当前用户信息
    path('get_user_info', views.get_user_info),  # 返回查看用户自己的门户信息
]
