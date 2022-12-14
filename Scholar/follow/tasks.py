from Scholar.celery import app
from follow.models import Follow
from user.models import FollowOfUser
from utils.Redis_utils import *


@app.task
def celery_add_follow(user_id, author_id):
    # 创建关注
    Follow.objects.create(user_id=user_id, author_id=author_id)

    follow_of_user = FollowOfUser.objects.get(id=user_id)

    # 修改数据库表项
    follow_id_list = eval(follow_of_user.follow_id_list)
    follow_id_list.append(author_id)
    follow_of_user.follow_id_list = str(follow_id_list)
    follow_of_user.save()

    cache_set_after_create('user', 'followofuser', follow_of_user.id, follow_of_user.to_dic())


@app.task
def celery_delete_follow(user_id, author_id):
    try:
        Follow.objects.get(user_id=user_id, author_id=author_id).delete()
    except:
        # print("已经完成了删除！")

    follow_of_user = FollowOfUser.objects.get(id=user_id)

    follow_id_list = eval(follow_of_user.follow_id_list)
    follow_id_list.remove(author_id)
    follow_of_user.follow_id_list = str(follow_id_list)
    follow_of_user.save()
