import json

from django.core.cache import cache
from django.http import JsonResponse
from history.tasks import *
from utils.Login_utils import login_checker

from utils.Redis_utils import cache_get_by_id


@login_checker
def update_history(request):
    if request.method == 'POST':
        user_id = request.user_id
        # 获取表单信息
        data_json = json.loads(request.body.decode())

        history_list = data_json.get('history_list', [])
        history_key, history_dict = cache_get_by_id('history', 'history', user_id)

        history_list = [history_list_info for history_list_info in history_list if history_list_info != ""]

        # 修改缓存
        history_dict['history_list'] = history_list
        cache.set(history_key, history_dict)

        # 修改数据库
        celery_update_history.delay(user_id, history_list)
        result = {'result': 1, 'message': r"更新历史记录成功！", "history_list": history_list}
        return JsonResponse(result)

    else:
        result = {'result': 0, 'message': r"请求方式错误！"}
        return JsonResponse(result)
