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
    print(user_id)
    message_id_list_key, message_id_list_dic = cache_get_by_id('message', 'usermessageidlist', user_id)
    user_key, user_dic = cache_get_by_id('user', 'user', user_id)
    user_dic['unread_message_count'] = 0
    cache.set(user_key, user_dic)
    celery_zero_user_unread_message_count.delay(user_id)
    message_list = []
    for message_id in message_id_list_dic["message_id_list"]:
        message_key, message_dic = cache_get_by_id('message', 'message', message_id)
        send_id = message_dic['send_id']

        if send_id != 0:
            try:
                user_key, user_dic = cache_get_by_id('user', 'user', send_id)
            except:
                continue
            message_dic['send_name'] = user_dic['username']
        else:
            message_dic['send_name'] = '管理员'

        message_list.append(message_dic)
    message_list.reverse()
    return JsonResponse({'result': 1, 'message': '获得用户消息列表成功', 'message_list': message_list})


@login_checker
def delete_message(request):
    data_json = json.loads(request.body.decode())
    print(data_json)
    user_id = request.user_id
    message_id_list = data_json.get('message_id_list')
    try:
        message_id_list_key, message_id_list_dic = cache_get_by_id('message', 'usermessageidlist', user_id)
    except:
        return JsonResponse({'result': 0, 'message': '此用户无消息列表'})
    for message_id in message_id_list:
        message_id_list_dic['message_id_list'].remove(message_id)
        cache.delete('message:' + 'message:' + str(message_id))
        celery_delete_message.delay(message_id)
    celery_remove_message_id.delay(user_id, message_id_list)
    cache.set(message_id_list_key, message_id_list_dic)
    return JsonResponse({'result': 1, 'message': '删除消息成功'})


@login_checker
def look_unread_message_count(request):
    data_json = json.loads(request.body.decode())
    print(data_json)
    user_id = request.user_id
    user_key, user_dic = cache_get_by_id('user', 'user', user_id)
    return JsonResponse(
        {'result': 1, 'message': '获取未读消息个数成功', 'unread_message_count': user_dic['unread_message_count']})


def message_test_send(request):
    if request.method == 'POST':
        data_json = json.loads(request.body.decode())
        send_id = int(data_json.get('send_id', 0))
        receiver_id = int(data_json.get('receiver_id', 0))
        message_type = int(data_json.get('message_type', 0))
        author_id = data_json.get('author_id', '')
        real_name = data_json.get('real_name', '')
        institution = data_json.get('institution', '')
        work_name = data_json.get('work_name', '')
        work_open_alex_id = data_json.get('work_open_alex_id', '')
        content = data_json.get('content', '')
        reply = data_json.get('reply', '')
        pdf = data_json.get('pdf', '')
        url = data_json.get('url', '')

        message = Message.objects.create(
            send_id=send_id,
            receiver_id=receiver_id,
            message_type=message_type,
            author_id=author_id,
            real_name=real_name,
            institution=institution,
            work_name=work_name,
            work_open_alex_id=work_open_alex_id,
            content=content,
            reply=reply,
            pdf=pdf,
            url=url
        )
        user = User.objects.get(id=receiver_id)

        user_key, user_dic = cache_get_by_id('user', 'user', receiver_id)
        user_dic['unread_message_count'] = user_dic['unread_message_count'] + 1  # 更新被评论用户的未读信息
        cache.set(user_key, user_dic)

        message_id_list_key, message_id_list_dic = cache_get_by_id('message', 'usermessageidlist', receiver_id)
        message_id_list_dic['message_id_list'].append(message.id)
        cache.set(message_id_list_key, message_id_list_dic)

        user_message_list = UserMessageIdList.objects.get(id=user.id)
        message_id_list = eval(user_message_list.message_id_list)
        message_id_list.append(message.id)
        user_message_list.message_id_list = str(message_id_list)
        user_message_list.save()

        user.unread_message_count += 1
        user.save()
        result = {
            'result': 1,
            'message': message.to_dic(),
            'user_message_list': user_message_list.message_id_list
        }
        return JsonResponse(result)

    else:
        result = {'result': 0, 'message': r"请求方式错误！"}
        return JsonResponse(result)
