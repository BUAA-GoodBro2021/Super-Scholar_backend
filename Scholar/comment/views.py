from django.core.cache import cache

from comment.models import Comment
from comment.tasks import *
from comment.utils import get_all_comments_by_work_id
from utils.Redis_utils import *

from utils.Sending_utils import *
from message.models import *
from form.tasks import *


@login_checker
def add_comment(request):
    if request.method == 'POST':
        # 获取表单信息
        data_json = json.loads(request.body.decode())
        user_id = request.user_id
        work_id = data_json.get('work_id')
        work_name = data_json.get('work_name')
        content = data_json.get('content')

        # 异常处理
        # 评论内容为空
        if len(content) == 0:
            result = {'result': 0, 'message': r"评论内容为空！"}
            return JsonResponse(result)

        # 创建数据
        comment = Comment.objects.create(user_id=user_id, work_id=work_id, content=content, work_name=work_name)

        # 对于顶级评论而言，其对应的祖先id就为其本身。
        comment.ancestor_id = comment.id
        comment.save()

        # 更新缓存
        cache_set_after_create("comment", "comment", comment.id, comment.to_dic())

        # 延迟更新数据库
        add_comment_of_work.delay(comment.id, work_id)

        result = {'result': 1, 'message': r"添加成功！"}
        return JsonResponse(result)



    else:
        result = {'result': 0, 'message': r"请求方式错误！"}
        return JsonResponse(result)


# 获取当前文章的全部评论
def get_all_comments(request):
    if request.method == 'POST':
        # 获取表单信息
        data_json = json.loads(request.body.decode())
        work_id = data_json.get('work_id')

        all_comments = get_all_comments_by_work_id(work_id)

        result = {'result': 1, 'message': r"查找成功！", 'all_comments': all_comments}
        return JsonResponse(result)



    else:
        result = {'result': 0, 'message': r"请求方式错误！"}
        return JsonResponse(result)


# 回复评论
@login_checker
def reply_comment(request):
    if request.method == 'POST':
        data_json = json.loads(request.body.decode())
        user_id = request.user_id
        work_id = data_json.get('work_id')
        content = data_json.get('content')
        comment_id = int(data_json.get('comment_id'))  # father_comment_id

        # 异常处理
        # 评论内容为空
        if len(content) == 0:
            result = {'result': 0, 'message': r"评论内容为空！"}
            return JsonResponse(result)

        # 获取父评论信息
        father_comment_key, father_comment_dic = cache_get_by_id('comment', 'comment', comment_id)
        work_name = father_comment_dic['work_name']

        # 获取被评论用户的用户信息
        reply_user_id = father_comment_dic['user_id']
        reply_user_key, reply_user_dic = cache_get_by_id('user', 'user', reply_user_id)

        # 创建数据——发送站内信，添加评论
        message = Message.objects.create(
            send_id=user_id,
            receiver_id=reply_user_id,
            message_type=4,
            work_name=work_name,
            work_open_alex_id=work_id,
            content=father_comment_dic['content'],
            reply=content,
        )
        comment = Comment.objects.create(
            level=1,
            user_id=user_id,
            work_id=work_id,
            work_name=work_name,
            content=content,
            father_id=comment_id,
            reply_user_id=reply_user_id,
            ancestor_id=father_comment_dic['ancestor_id']
        )

        # 更新缓存
        reply_user_dic['unread_message_count'] = reply_user_dic['unread_message_count'] + 1  # 更新被评论用户的未读信息
        cache.set(reply_user_key, reply_user_dic)

        cache_set_after_create('message', 'message', message.id, message.to_dic())  # 添加message缓存
        cache_set_after_create("comment", "comment", comment.id, comment.to_dic())  # 添加comment缓存

        message_id_list_key, message_id_list_dic = cache_get_by_id('message', 'usermessageidlist', reply_user_id)
        message_id_list_dic['message_id_list'].append(message.id)
        cache.set(message_id_list_key, message_id_list_dic)

        # 延迟更新数据库
        add_comment_of_comment.delay(comment.id, comment_id)
        celery_add_user_message_id_list.delay(reply_user_id, message.id)
        celery_add_unread_message_count(reply_user_id)

        result = {'result': 1, 'message': r"添加成功！"}
        return JsonResponse(result)


    else:
        result = {'result': 0, 'message': r"请求方式错误！"}
        return JsonResponse(result)


# 删除评论
@login_checker
def delete_comment(request):
    if request.method == 'POST':
        data_json = json.loads(request.body.decode())
        user_id = request.user_id
        comment_id = int(data_json.get('comment_id'))

        # 获取当前评论的信息
        try:
            comment_key, comment = cache_get_by_id('comment', 'comment', comment_id)
        except:
            result = {'result': 0, 'message': r"该条评论已被删除！"}
            return JsonResponse(result)

        # 异常处理
        # 当前用户不是该评论的评论者
        if user_id != comment['user_id']:
            result = {'result': 0, 'message': r"您无法删除他人的评论！"}
            return JsonResponse(result)

        # 如果当前评论是顶级评论，则应该彻底删除
        if comment['level'] == 0:
            # 修改当前文章的缓存数据
            work_id = comment['work_id']
            print("work id is ", work_id)

            comment_of_work_key, comment_of_work = cache_get_by_id('comment', 'commentofworks', work_id)
            print(comment_of_work['comment_id_list'])

            comment_of_work['comment_id_list'].remove(comment_id)

            cache.set(comment_of_work_key, comment_of_work)

            # 删除当前评论的缓存数据
            cache_del_by_id('comment', 'comment', comment_id)
            # 删除当前评论的子级评论信息缓存
            cache_del_by_id('comment', 'commentofcomments', comment_id)


        else:
            # 删除当前评论的缓存数据
            cache_del_by_id('comment', 'comment', comment_id)

        delay_delete_comment.delay(comment_id, comment['work_id'], comment['level'])
        result = {'result': 1, 'message': r"删除成功！"}
        return JsonResponse(result)


    else:
        result = {'result': 0, 'message': r"请求方式错误！"}
        return JsonResponse(result)


def reset_all_comment(request):
    if request.method == 'POST':
        works = CommentOfWorks.objects.all()
        for work in works:
            work_id = work.id
            comment_id_list = ""
            comments = Comment.objects.filter(work_id=work_id).all()
            for comment in comments:
                comment_id_list += str(comment.id) + ' '

            work.comment_id_list = comment_id_list
            work.save()

        comments = CommentOfComments.objects.all()
        for comment in comments:
            comment_id = comment.id
            comment_id_list = ""
            son_comments = Comment.objects.filter(father_id=comment_id).all()
            for som_comment in son_comments:
                comment_id_list += str(som_comment.id) + ' '

            comment.comment_id_list = comment_id_list
            comment.save()

        result = {'result': 1, 'message': r"Reset all!"}
        return JsonResponse(result)

    else:
        result = {'result': 0, 'message': r"请求方式错误！"}
        return JsonResponse(result)
