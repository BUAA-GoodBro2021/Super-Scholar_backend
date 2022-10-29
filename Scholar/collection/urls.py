from django.urls import path

from collection import views

urlpatterns = [
    path('add_collection_package', views.add_collection_package),
    path('change_package_name', views.change_package_name),
    path('collect_work', views.collect_work),
    path('cancel_work', views.cancel_work),

    # path("get_index_data_view", views.get_index_data),
]