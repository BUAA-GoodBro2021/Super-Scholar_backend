from django.http import HttpResponse
from django.shortcuts import render
import random
from properties import *
from utils.tasks import *
from utils.Login_utils import *
from utils.Redis_utils import *


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

        # 激活用户 验证邮箱
        user_dict['is_active'] = True
        user_dict['email'] = email

        # 设置随机头像
        avatar_url = default_avatar_url_match + str(random.choice(range(1, 31))) + '.png'
        user_dict['avatar_url'] = avatar_url
        # 同步缓存
        cache.set(user_key, user_dict)
        # 同步mysql
        celery_activate_user.delay(user_id, email, avatar_url)

        # TODO 发送站内信

        # 返回注册成功的界面
        content["title"] = "感谢注册"
        content["message"] = "注册Summer平台成功！"
        return render(request, 'EmailContent-check.html', content)

    # 重设密码
    if 'password' in payload.keys():
        password = payload.get('password')

        # 同步mysql(password不在缓存里面)
        # celery_change_password.delay(user_id, password)
        # 需要立即修改，使用异步不合适
        user = User.objects.get(id=user_id)
        user.password = password
        user.save()

        # TODO 发送站内信

        # 返回修改成功的界面
        content["title"] = "修改成功"
        content["message"] = "修改密码成功！"
        return render(request, 'EmailContent-check.html', content)