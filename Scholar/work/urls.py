from django.urls import path

from work import views

urlpatterns = [
    path('user_upload_pdf', views.user_upload_pdf),  # 用户上传pdf
    path('manager_check_upload_pdf', views.manager_check_upload_pdf),  # 管理员查看未处理申请
    path("manager_deal_upload_pdf", views.manager_deal_upload_pdf),  # 管理员处理上传pdf申请
    path('user_re_upload_pdf', views.user_re_upload_pdf),  # 用户重新上传pdf
]
