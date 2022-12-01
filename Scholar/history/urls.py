from django.urls import path

from history import views

urlpatterns = [
    path('update_history', views.update_history),  # 更新历史记录
]
