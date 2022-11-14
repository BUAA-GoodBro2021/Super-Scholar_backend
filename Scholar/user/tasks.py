from user.models import User
from Scholar.celery import app


@app.task
def celery_change_introduction(user_id, introduction):
    user = User.objects.get(id=user_id)
    user.introduction = introduction
    user.save()
    return user.to_dic()
