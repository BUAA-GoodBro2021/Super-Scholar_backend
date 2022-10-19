from django.urls import path

from search import views

urlpatterns = [
    # 主页部分
    path("get_index_data_view", views.get_index_data_view),
    path("associate_content_view", views.associate_content_view),

    # 实体详情
    path("get_single_work_data_view", views.get_single_work_data_view),

    # 筛选实体
    path("get_list_of_works_data_view", views.get_list_of_works_data_view),

]
