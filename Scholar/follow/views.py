from follow.models import Follow

from utils.Sending_utils import *


@login_checker
def follow_author(request):
    if request.method == 'POST':
        # 获取表单信息
        data_json = json.loads(request.body.decode())
        user_id = request.user_id
        author_id = data_json.get('author_id')

        # 处理异常信息
        if Follow.objects.filter(user_id=user_id, author_id=author_id).exists():
            result = {'result': 0, 'message': r"您已关注该作者！"}
            return JsonResponse(result)

        Follow.objects.create(user_id=user_id, author_id=author_id)
        result = {'result': 1, 'message': r"关注成功！"}
        return JsonResponse(result)

    else:
        result = {'result': 0, 'message': r"请求方式错误！"}
        return JsonResponse(result)


@login_checker
def unfollow_author(request):
    if request.method == 'POST':
        # 获取表单信息
        data_json = json.loads(request.body.decode())
        user_id = request.user_id
        author_id = data_json.get('author_id')

        follow_message = Follow.objects.filter(user_id=user_id, author_id=author_id)

        # 处理异常信息
        if not follow_message.exists():
            result = {'result': 0, 'message': r"您已取消关注该作者！"}
            return JsonResponse(result)

        follow_message.delete()
        result = {'result': 1, 'message': r"取消关注成功！"}
        return JsonResponse(result)

    else:
        result = {'result': 0, 'message': r"请求方式错误！"}
        return JsonResponse(result)


@login_checker
def follow_list(request):
    if request.method == 'POST':
        # 获取表单信息
        user_id = request.user_id

        follow_list = Follow.objects.filter(user_id=user_id)

        follow_id_list = [follow_message.author_id for follow_message in follow_list]

        result = {'result': 1, 'message': r"查找成功！", "follow_id_list": follow_id_list}
        return JsonResponse(result)

    else:
        result = {'result': 0, 'message': r"请求方式错误！"}
        return JsonResponse(result)
