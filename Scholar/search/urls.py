from django.urls import path

from search import views

urlpatterns = [
    # 主页部分
    path("get_index_data_view", views.get_index_data_view),
    path("associate_content_view", views.associate_content_view),

    # 实体详情
    path("get_single_data_view", views.get_single_data_view),

    # 筛选实体
    path("get_list_of_data_view", views.get_list_of_data_view),

    # 分组实体
    path("get_groups_of_data_view", views.get_groups_of_data_view),

    # 高级检索
    path("advanced_search_view", views.advanced_search_view),

]
