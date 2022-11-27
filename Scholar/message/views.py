from django.shortcuts import render
from django.utils.timezone import now

from .tasks import *
from form.models import *
from utils.Redis_utils import *
from utils.Sending_utils import *
from django.core.cache import cache
from message.models import *


# Create your views here.
@login_checker
def look_message_list(request):
    data_json = json.loads(request.body.decode())
    print(data_json)
    user_id = request.user_id
    message_id_list_key, message_id_list_dic = cache_get_by_id('message', 'usermessageidlist', user_id)
    user_key, user_dic = cache_get_by_id('user', 'user', user_id)
    user_dic['unread_message_count'] = 0
    cache.set(user_key, user_dic)
    celery_zero_user_unread_message_count.delay(user_id)
    message_list = []
    for message_id in message_id_list_dic["message_id_list"]:
        message_key, message_dic = cache_get_by_id('message', 'message', message_id)
        message_list.append(message_dic)
    message_list.reverse()
    return JsonResponse({'result': 1, 'message': '获得用户消息列表成功', 'message_list': message_list})

@login_checker
def delete_message(request):
    data_json = json.loads(request.body.decode())
    print(data_json)
    user_id = request.user_id
    message_id = data_json.get('message_id')
    try:
        message_id_list_key, message_id_list_dic = cache_get_by_id('message', 'usermessageidlist', user_id)
    except:
        return JsonResponse({'result': 0, 'message': '此用户无消息列表'})
    message_id_list_dic['message_id_list'].remove(message_id)
    cache.set(message_id_list_key, message_id_list_dic)
    celery_remove_message_id.delay(user_id, message_id)
    cache.delete('message:' + 'message:' + str(message_id))
    celery_delete_message.delay(message_id)
    return JsonResponse({'result': 1, 'message': '删除消息成功'})
