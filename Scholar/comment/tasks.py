from comment.models import *
from Scholar.celery import app
from utils.Redis_utils import *


@app.task
def add_comment_of_work(comment_id, work_id):
    # 如果表中已有对当前work的记录，则直接获取；否则进行添加。
    try:
        comment_of_work = ComnentOfWorks.objects.get(id=work_id)
    except:
        comment_of_work = ComnentOfWorks.objects.create(id=work_id)

    comment_of_work.comment_id_list += ' ' + str(comment_id)
    comment_of_work.save()
    cache_set_after_create('comment', 'comnentofworks', comment_of_work.id, comment_of_work.to_dic())


@app.task
def add_comment_of_comment(comment_id, father_comment_id):
    # 如果表中已有对当前comment的记录，则直接获取；否则进行添加。
    try:
        comment_of_comment = ComnentOfWorks.objects.get(id=father_comment_id)
    except:
        comment_of_comment = ComnentOfWorks.objects.create(id=father_comment_id)

    comment_of_comment.comment_id_list += ' ' + str(comment_id)
    comment_of_comment.save()
    cache_set_after_create('comment', 'comnentofcomments', comment_of_comment.id, comment_of_comment.to_dic())
