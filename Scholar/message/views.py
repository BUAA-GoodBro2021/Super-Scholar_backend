from django.shortcuts import render
from django.utils.timezone import now

from form.tasks import *
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
    message_list = []
    for message_id in message_id_list_dic["message_id_list"]:
        message_key, message_dic = cache_get_by_id('message', 'message', message_id)
        message_list.append(message_dic)
    return JsonResponse({'result': 1, 'message': '获得用户消息列表成功', 'message_list': message_list})
