from Scholar.celery import app
from form.models import *
from user.models import *
from message.models import *


@app.task
def celery_zero_user_unread_message_count(user_id):
    this_user = User.objects.get(id=user_id)
    this_user.unread_message_count = 0
    this_user.save()
    print('celery_zero_user_unread_message_count')
