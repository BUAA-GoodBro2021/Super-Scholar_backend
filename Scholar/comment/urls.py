from django.urls import path

from comment import views

urlpatterns = [
    path('add_comment', views.add_comment),
    path('get_all_comments', views.get_all_comments),
    path('reply_comment', views.reply_comment),
    path('delete_comment', views.delete_comment),
    path('reset_all_comment', views.reset_all_comment),
]