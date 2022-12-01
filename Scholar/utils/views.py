from django.http import HttpResponse
from django.shortcuts import render
import random

from form.tasks import celery_add_unread_message_count, celery_add_user_message_id_list
from history.models import History
from properties import *
from utils.tasks import *
from utils.Login_utils import *
from utils.Redis_utils import *
from message.models import *


def clear_redis_all(request):
    cache.clear()
    return HttpResponse("OK")


# 通过邮箱激活用户
def active(request, token):
    """
    :param request: 请求体
    :param token:   登录令牌
    :return:        各种情况的邮件主页渲染
    """
    # 校验令牌
    payload = check_token(token)

    # 邮件信息
    content = {'url': production_base_url}

    # 校验失败
    if payload is None:
        content["title"] = "操作失败"
        content["message"] = "链接失效啦！"
        return render(request, 'EmailContent-check.html', content)

    # 获取邮件中的信息
    user_id = payload.get('user_id')

    # 获取用户信息
    try:
        user_key, user_dict = cache_get_by_id('user', 'user', user_id)
    except Exception:
        # 返回修改成功的界面
        content["title"] = "激活失败"
        content["message"] = "啊偶，用户名好像已经被注册啦，再去挑选一个你喜欢的用户名叭！"
        return render(request, 'EmailContent-check.html', content)

    # 使用邮箱激活账号
    if 'email' in payload.keys():
        email = payload.get('email')

        # 防止同一邮箱反复激活
        if User.objects.filter(email=email, is_active=True).exists():
            content["title"] = "激活失败"
            content["message"] = "啊偶，该邮箱已经被激活过啦，一个邮箱只能绑定一个用户哦！"
            return render(request, 'EmailContent-check.html', content)

        # 激活用户 验证邮箱
        user_dict['is_active'] = True
        user_dict['email'] = email

        # 设置随机头像
        avatar_url = default_avatar_url_match + str(random.choice(range(1, 31))) + '.png'

        # 发送站内信
        message = Message.objects.create(send_id=0, receiver_id=user_id, message_type=5)

        # 同步缓存
        user_dict['avatar_url'] = avatar_url
        user_dict['unread_message_count'] = user_dict['unread_message_count'] + 1  # 更新被评论用户的未读信息
        cache.set(user_key, user_dict)

        cache_set_after_create('message', 'message', message.id, message.to_dic())  # 添加message缓存

        # 同步mysql
        celery_add_unread_message_count(user_id)
        celery_activate_user.delay(user_id, email, avatar_url)

        # 返回注册成功的界面
        content["title"] = "感谢注册"
        content["message"] = "注册 Super Scholar 学术成功分享平台成功！"
        try:
            this_UserMessageIdList = UserMessageIdList.objects.create(id=int(user_id), message_id_list='[]')
        except:
            return JsonResponse({'result': 0, 'message': '不能重复点击哦'})
        cache_set_after_create('message', 'usermessageidlist', this_UserMessageIdList.id,
                               this_UserMessageIdList.to_dic())

        # 同步站内信列表缓存
        message_id_list_key, message_id_list_dic = cache_get_by_id('message', 'usermessageidlist', user_id)
        message_id_list_dic['message_id_list'].append(message.id)
        cache.set(message_id_list_key, message_id_list_dic)

        # 同步站内信
        celery_add_user_message_id_list.delay(user_id, message.id)

        try:
            history = History.objects.create(id=int(user_id))
        except:
            return JsonResponse({'result': 0, 'message': '不能重复点击哦'})
        # 创建每一个人的历史记录
        cache_set_after_create('history', 'history', history.id, history.to_dic())

        user_id_list_key, user_id_list_dic = cache_get_by_id('user', 'userlist', 0)
        user_id_list_dic['id_list'].append(int(user_id))
        cache.set(user_id_list_key, user_id_list_dic)
        celery_add_user_id.delay(int(user_id))
        return render(request, 'EmailContent-check.html', content)

    # 重设密码
    elif 'password' in payload.keys():
        password = payload.get('password')
        email = payload.get('email')

        # 同步mysql(password不在缓存里面)
        # celery_change_password.delay(user_id, password)
        # 需要立即修改，使用异步不合适
        user = User.objects.get(id=user_id)
        user.password = password
        user.save()

        # 发送站内信
        message = Message.objects.create(send_id=0, receiver_id=user_id, message_type=6)

        # 同步缓存
        user_dict['unread_message_count'] = user_dict['unread_message_count'] + 1  # 更新被评论用户的未读信息
        cache.set(user_key, user_dict)

        cache_set_after_create('message', 'message', message.id, message.to_dic())  # 添加message缓存

        message_id_list_key, message_id_list_dic = cache_get_by_id('message', 'usermessageidlist', user_id)
        message_id_list_dic['message_id_list'].append(message.id)
        cache.set(message_id_list_key, message_id_list_dic)

        # 同步mysql
        celery_add_user_message_id_list.delay(user_id, message.id)
        celery_add_unread_message_count(user_id)

        # 返回修改成功的界面
        content["title"] = "修改成功"
        content["message"] = "修改密码成功！"
        return render(request, 'EmailContent-check.html', content)
