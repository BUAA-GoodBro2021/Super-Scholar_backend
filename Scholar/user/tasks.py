from user.models import User, UserList
from Scholar.celery import app


@app.task
def celery_change_introduction(user_id, introduction, username):
    user = User.objects.get(id=user_id)
    user.introduction = introduction
    user.username = username
    user.save()
    return user.to_dic()


@app.task()
def celery_add_user_id(user_id):
    user_id_list = UserList.objects.get(id=0)
    id_list = eval(user_id_list.id_list)
    id_list.append(user_id)
    user_id_list.id_list = str(id_list)
    user_id_list.save()
    print("celery_add_user_id")
