from Scholar.celery import app
from form.models import *
from user.models import *
from message.models import *


@app.task
def celery_zero_user_unread_message_count(user_id):
    this_user = User.objects.get(id=user_id)
    this_user.unread_message_count = 0
    this_user.save()
    # print('celery_zero_user_unread_message_count')


@app.task
def celery_remove_message_id(user_id, message_id_list):
    user_message_list = UserMessageIdList.objects.get(id=user_id)
    db_message_id_list = eval(user_message_list.message_id_list)
    for message_id in message_id_list:
        db_message_id_list.remove(message_id)
    user_message_list.message_id_list = str(db_message_id_list)
    user_message_list.save()
    # print('celery_remove_message_id')


@app.task
def celery_delete_message(message_id):
    this_message = Message.objects.get(id=message_id)
    this_message.delete()
    # print('celery_delete_message')
