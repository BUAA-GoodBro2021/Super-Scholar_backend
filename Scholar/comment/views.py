from django.core.cache import cache

from comment.models import Comment
from comment.tasks import *
from comment.utils import get_all_comments_by_work_id
from utils.Redis_utils import *

from utils.Sending_utils import *


@login_checker
def add_comment(request):
    if request.method == 'POST':
        # 获取表单信息
        data_json = json.loads(request.body.decode())
        user_id = request.user_id
        work_id = data_json.get('work_id')
        content = data_json.get('content')

        # 异常处理
        # 评论内容为空
        if len(content) == 0:
            result = {'result': 0, 'message': r"评论内容为空！"}
            return JsonResponse(result)

        # 创建数据
        comment = Comment.objects.create(user_id=user_id, work_id=work_id, content=content)

        # 对于顶级评论而言，其对应的祖先id就为其本身。
        comment.ancestor_id = comment.id
        comment.save()

        # 更新缓存
        cache_set_after_create("comment", "comment", comment.id, comment.to_dic())

        # 延迟更新数据库
        add_comment_of_work(comment.id, work_id)

        result = {'result': 0, 'message': r"添加成功！"}
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

        result = {'result': 0, 'message': r"查找成功！", 'all_comments': all_comments}
        return JsonResponse(result)



    else:
        result = {'result': 0, 'message': r"请求方式错误！"}
        return JsonResponse(result)


# 回复评论
def reply_comment(request):
    if request.method == 'POST':
        data_json = json.loads(request.body.decode())
        user_id = request.user_id
        work_id = data_json.get('work_id')
        content = data_json.get('content')
        comment_id = data_json.get('comment_id')  # father_comment_id

        # 异常处理
        # 评论内容为空
        if len(content) == 0:
            result = {'result': 0, 'message': r"评论内容为空！"}
            return JsonResponse(result)

        # 获取父评论信息
        father_comment_key, father_comment_dic = cache_get_by_id('comment', 'comment', comment_id)

        # 创建数据
        comment = Comment.objects.create(user_id=user_id, work_id=work_id, content=content,
                                         father_id=comment_id,
                                         ancestor_id=father_comment_dic['ancestor_id'])
        # 更新缓存
        cache_set_after_create("comment", "comment", comment.id, comment.to_dic())

        # 延迟更新数据库
        add_comment_of_comment(comment.id, comment_id)

        result = {'result': 0, 'message': r"添加成功！"}
        return JsonResponse(result)


    else:
        result = {'result': 0, 'message': r"请求方式错误！"}
        return JsonResponse(result)
