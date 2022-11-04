from comment.models import *
from Scholar.celery import app
from utils.Redis_utils import *


@app.task
def add_comment_of_work(comment_id, work_id):
    try:
        comment_of_work = ComnentOfWorks.objects.get(id=work_id)
    except:
        comment_of_work = ComnentOfWorks.objects.create(id=work_id)
    comment_of_work.comment_id_list += ' ' + str(comment_id)
    comment_of_work.save()
    cache_set_after_create('comment', 'comnentofworks', comment_of_work.id, comment_of_work.to_dic())
