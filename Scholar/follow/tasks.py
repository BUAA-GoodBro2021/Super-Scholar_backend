from Scholar.celery import app
from follow.models import Follow
from user.models import FollowOfUser
from utils.Redis_utils import *

@app.task
def celery_add_follow(user_id, author_id):
    Follow.objects.create(user_id=user_id, author_id=author_id)

    try:
        follow_of_user = FollowOfUser.objects.get(id=user_id)
    except:
        follow_of_user = FollowOfUser.objects.create(id=user_id)

    follow_of_user.follow_id_list += author_id + '#'
    follow_of_user.save()
    cache_set_after_create('user', 'followofuser', follow_of_user.id, follow_of_user.to_dic())


@app.task
def celery_delete_follow(user_id, author_id):
    try:
        Follow.objects.get(user_id=user_id, author_id=author_id).delete()
    except:
        print("已经完成了删除！")

    follow_of_user = FollowOfUser.objects.get(id=user_id)
    follow_list = follow_of_user.to_dic()['follow_id_list']
    print(follow_list)

    follow_list.remove(author_id)
    follow_list = '#'.join(follow_list)
    follow_of_user.follow_id_list = follow_list
    follow_of_user.save()
