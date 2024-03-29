from django.urls import path

from collection import views

urlpatterns = [
    path('add_collection_package', views.add_collection_package),
    path('change_package_name', views.change_package_name),
    path('collect_work', views.collect_work),
    path('cancel_work', views.cancel_work),
    path('delete_collection_package', views.delete_collection_package),
    path('get_collection_package_list', views.get_collection_package_list),
    path('get_collection_package_by_id', views.get_collection_package_by_id),

    # path("get_index_data_view", views.get_index_data),
]