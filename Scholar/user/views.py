import json

from user.models import *
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
# Create your views here.
from utils.Login_utils import hash_encode

from utils.Sending_utils import *


def test(request):
    return HttpResponse("Hello world!")

# 用户注册
def register( request ):
    """
    :param request: 请求体
    :return:        1 - 成功， 0 - 失败

    请求体包含包含 username，password1，password2，email
    """
    if request.method == 'POST':
        data_json = json.loads(request.body.decode())

        print( data_json)
        username = data_json.get('username', '')
        password1 = data_json.get('password1', '')
        password2 = data_json.get('password2', '')
        email = data_json.get('email', '')

        if len(username) == 0 or len(password1) == 0 or len(password2) == 0 or len(email) == 0:
            result = {
                'result': 0,
                'message': r'用户名, 邮箱, 与密码不允许为空!'
            }
            return JsonResponse( result )
        if User.objects.filter(username=username, is_active=True).exists():
            result = {
                'result': 0,
                'message': r'用户已存在!'
            }
            return JsonResponse(result)
        if password1 != password2:
            result = {
                'result': 0,
                'message': r'两次密码不一致!'
            }
            return JsonResponse(result)

        user = User.objects.create(
            username=username,
            email=email,
            password=hash_encode(password1),
            is_active=False
        )

        payload = {
            'user_id': user.id,
            'email': email,
        }

        send_result = send_email(payload, email, 'register')
        if not send_result:
            result = {'result': 0, 'message': r'发送失败!请检查邮箱格式'}
            return JsonResponse(result)
        else:
            result = {'result': 1, 'message': r'发送成功!请及时在邮箱中查收.'}
            return JsonResponse(result)


    else:
        result = {'result': 0, 'message': r"请求方式错误！"}
        return JsonResponse(result)


def login( request ):

    pass
