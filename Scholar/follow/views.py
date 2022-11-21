from follow.models import Follow
from django.core.cache import cache
from utils.Sending_utils import *
from follow.tasks import *


@login_checker
def follow_author(request):
    if request.method == 'POST':
        # 获取表单信息
        data_json = json.loads(request.body.decode())
        user_id = request.user_id
        author_id = data_json.get('author_id')

        try:
            user_key, user_dic = cache_get_by_id('user', 'followofuser', user_id)

            # 处理异常信息
            if author_id in user_dic['follow_id_list']:
                result = {'result': 0, 'message': r"您已关注该作者！"}
                return JsonResponse(result)

            # 更新缓存
            user_dic['follow_id_list'].append(author_id)
            cache.set(user_key, user_dic)

        except:
            pass

        # 在数据库中建立表项
        celery_add_follow.delay(user_id, author_id)

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

        try:
            user_key, user_dic = cache_get_by_id('user', 'followofuser', user_id)

            # 处理异常信息
            if author_id not in user_dic['follow_id_list']:
                result = {'result': 0, 'message': r"您已取消关注该作者！"}
                return JsonResponse(result)

            # 更新缓存
            user_dic['follow_id_list'].remove(author_id)
            cache.set(user_key, user_dic)

            celery_delete_follow.delay(user_id, author_id)

        except:
            result = {'result': 0, 'message': r"您还未关注任何人！"}
            return JsonResponse(result)

        # 更新数据库

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

        try:
            user_key, user_dic = cache_get_by_id('user', 'followofuser', user_id)
            follow_id_list = user_dic['follow_id_list']

        except:
            follow_id_list = []

        result = {'result': 1, 'message': r"查找成功！", "follow_id_list": follow_id_list}
        return JsonResponse(result)

    else:
        result = {'result': 0, 'message': r"请求方式错误！"}
        return JsonResponse(result)
