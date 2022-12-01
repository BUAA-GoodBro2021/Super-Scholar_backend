from django.urls import path
from author import views

urlpatterns = [
    path('get_relate_net', views.get_relate_net),  # 用户申请认领门户

]
