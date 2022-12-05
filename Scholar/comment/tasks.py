from comment.models import *
from Scholar.celery import app
from utils.Redis_utils import *


@app.task
def add_comment_of_work(comment_id, work_id):
    # 如果表中已有对当前work的记录，则直接获取；否则进行添加。
    try:
        comment_of_work = CommentOfWorks.objects.get(id=work_id)
    except:
        comment_of_work = CommentOfWorks.objects.create(id=work_id)

    comment_id_list = eval(comment_of_work.comment_id_list)
    comment_id_list.append(comment_id)
    comment_of_work.comment_id_list = str(comment_id_list)
    comment_of_work.save()
    cache_set_after_create('comment', 'commentofworks', comment_of_work.id, comment_of_work.to_dic())


@app.task
def add_comment_of_comment(comment_id, father_comment_id):
    comment_of_comment = CommentOfComments.objects.get(id=father_comment_id)

    comment_id_list = eval(comment_of_comment.comment_id_list)
    comment_id_list.append(comment_id)
    comment_of_comment.comment_id_list = str(comment_id_list)

    comment_of_comment.save()


@app.task
def delay_delete_comment(comment_id, work_id, comment_level):
    print(comment_id, work_id, comment_level)

    if comment_level == 0:
        try:
            comment_of_comment = CommentOfComments.objects.get(id=comment_id)
            comment_of_comment.delete()
        except:
            print("Can't find the CommentOfComments!")

        try:
            comment_of_work = CommentOfWorks.objects.get(id=work_id)
            comment_list = eval(comment_of_work.comment_id_list)
            comment_list.remove(comment_id)
            comment_of_work.comment_id_list = str(comment_list)
            comment_of_work.save()


        except:
            print("Can't find the CommentOfWorks!")

        try:
            comment = Comment.objects.get(id=comment_id)
            comment.delete()
        except:
            print("Can't find the Comment!")

        try:
            comments = Comment.objects.filter(ancestor_id=comment_id).all()
            comments.delete()
        except:
            print("Can't find the son_comments!")

    elif comment_level == 1:
        try:
            comment = Comment.objects.get(id=comment_id)
            comment.is_deleted = True
            comment.save()
        except:
            print("Can't find the Comment!")
