import datetime
from Scholar.celery import app
from user.models import User


@app.task
def celery_activate_user(user_id, email, avatar_url):
    user = User.objects.get(id=user_id)
    user.is_active = True
    user.email = email
    user.avatar_url = avatar_url
    user.save()
    # 删除其他伪用户
    user_list = User.objects.filter(username=user.username, is_active=False)
    if user_list:
        user_list.delete()
    print('celery', datetime.datetime.now())
    return user.to_dic()
