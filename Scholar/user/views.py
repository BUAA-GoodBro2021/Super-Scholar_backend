from diophila import OpenAlex
from django.core.cache import cache
from user.models import *
from django.http import HttpResponse
from user.tasks import *

from utils.Sending_utils import *


def test(request):
    return HttpResponse("Hello world!")


# 用户注册
# TODO 密码强度检测。
def register(request):
    """
    :param request: 请求体
    :return:        1 - 成功， 0 - 失败

    请求体包含包含 username，password1，password2，email
    """
    if request.method == 'POST':
        data_json = json.loads(request.body.decode())
        print(data_json)

        username = data_json.get('username', '')
        password1 = data_json.get('password1', '')
        password2 = data_json.get('password2', '')
        email = data_json.get('email', '')

        if len(username) == 0 or len(password1) == 0 or len(password2) == 0 or len(email) == 0:
            result = {'result': 0, 'message': r'用户名, 邮箱, 与密码不允许为空!'}
            return JsonResponse(result)

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

        # 创建该用户的收藏夹
        CollectionOfUser.objects.create(id=user.id)

        payload = {'user_id': user.id, 'email': email}

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


def login(request):
    """
        :param request: 请求体
        :return:        1 - 成功， 0 - 失败

        请求体包含包含 username, password
    """
    if request.method == 'POST':

        # 获取表单信息
        data_json = json.loads(request.body.decode())
        print(data_json)
        username = data_json.get('username', '')
        password = data_json.get('password', '')

        # 检验错误情况
        if len(username) == 0 or len(password) == 0:
            result = {'result': 0, 'message': r'用户名与密码不允许为空!'}
            return JsonResponse(result)

        if not User.objects.filter(username=username, is_active=True).exists():
            result = {'result': 0, 'message': r'用户不存在!'}
            return JsonResponse(result)

        # 获取用户实体
        user = User.objects.get(username=username, is_active=True)

        if user.password != hash_encode(password):
            result = {'result': 0, 'message': r'用户名或者密码有误!'}
            return JsonResponse(result)

        # 需要加密的信息
        payload = {'user_id': user.id}
        # 签发登录令牌
        token = sign_token(payload, exp=3600 * 24000000)

        # 获取缓存信息
        user_key, user_dict = cache_get_by_id('user', 'user', user.id)

        result = {'result': 1, 'message': r"登录成功！", 'token': token, 'user': user_dict}
        return JsonResponse(result)

    else:
        result = {'result': 0, 'message': r"请求方式错误！"}
        return JsonResponse(result)


def find_password(request):
    """
        :param request: 请求体
        :return:        1 - 成功， 0 - 失败

        请求体包含包含 username, password1, password2, email
    """
    if request.method == 'POST':

        # 获取表单信息
        data_json = json.loads(request.body.decode())
        print(data_json)
        username = data_json.get('username', '')
        password1 = data_json.get('password1', '')
        password2 = data_json.get('password2', '')

        # 检测异常情况
        if not User.objects.filter(username=username).exists():
            result = {'result': 0, 'message': r'用户名不存在!'}
            return JsonResponse(result)

        if len(password1) == 0 or len(password2) == 0:
            result = {'result': 0, 'message': r'用户名与密码不允许为空!'}
            return JsonResponse(result)

        if password1 != password2:
            result = {'result': 0, 'message': r'两次密码不一致!'}
            return JsonResponse(result)

        # 获取该用户实体
        user = User.objects.get(username=username)
        email = user.email

        if user.password == hash_encode(password1):
            result = {'result': 0, 'message': r'修改前后密码相同!'}
            return JsonResponse(result)

        # 需要加密的信息
        payload = {'user_id': user.id, 'password': hash_encode(password1)}

        # 发送邮件
        send_result = send_email(payload, email, 'find')

        if not send_result:
            result = {'result': 0, 'message': r'发送失败!请检查邮箱格式'}
            return JsonResponse(result)
        else:
            result = {'result': 1, 'message': r'发送成功!请及时在邮箱中完成修改密码的确认.'}
            return JsonResponse(result)
    else:
        result = {'result': 0, 'message': r"请求方式错误！"}
        return JsonResponse(result)


# 编辑个人简介。
@login_checker
def edit_introduction(request):
    if request.method == 'POST':
        # 获取表单信息
        data_json = json.loads(request.body.decode())
        user_id = request.user_id
        introduction = data_json.get('introduction', 'Leave something to help others get to know you better!')

        # 获取信息
        user_key, user_dict = cache_get_by_id('user', 'user', user_id)
        # 修改信息，同步缓存
        user_dict['introduction'] = introduction
        cache.set(user_key, user_dict)
        # 修改数据库
        celery_change_introduction.delay(user_id, introduction)

        result = {'result': 1, 'message': r"修改成功！", 'user': user_dict}
        return JsonResponse(result)

    else:
        result = {'result': 0, 'message': r"请求方式错误！"}
        return JsonResponse(result)


# 返回当前用户信息
@login_checker
def get_other_user(request):
    if request.method == 'POST':
        # 获取用户id
        data_json = json.loads(request.body.decode())
        user_id = int(data_json.get('user_id', 0))

        # 获取用户信息
        try:
            user_key, user_dict = cache_get_by_id('user', 'user', user_id)
            result = {'result': 1, 'message': r"查找成功！", 'user': user_dict}
        except:
            result = {'result': 0, 'message': r"查找失败！"}

        return JsonResponse(result)

    else:
        result = {'result': 0, 'message': r"请求方式错误！"}
        return JsonResponse(result)


@login_checker
def get_user(request):
    if request.method == 'POST':
        # 获取用户id
        user_id = request.user_id

        # 获取用户信息
        user_key, user_dict = cache_get_by_id('user', 'user', user_id)
        result = {'result': 1, 'message': r"查找成功！", 'user': user_dict}
        return JsonResponse(result)

    else:
        result = {'result': 0, 'message': r"请求方式错误！"}
        return JsonResponse(result)


# 查看用户自己的门户信息
@login_checker
def get_user_info(request):
    if request.method == 'POST':

        # 获取表单信息
        data_json = json.loads(request.body.decode())
        # 获取到需要查询的页数以及每页多少个
        pages = data_json.get('page', '')
        per_page = data_json.get('per_page', '')

        # 获取用户id
        user_id = request.user_id
        # 获取信息
        user_key, user_dict = cache_get_by_id('user', 'user', user_id)

        # 获取到作者的 open_alex_id
        is_professional = user_dict['is_professional']
        open_alex_id = user_dict['open_alex_id']

        # 判断是否为已经认领门户的用户
        if is_professional != 1:
            result = {'result': 0, 'message': r"您暂时没有认领门户或者正在申请门户，请成功认领门户之后再尝试！"}
            return JsonResponse(result)

        # 通过open_alex_id获取到其文章列表
        open_alex = OpenAlex("zhouenshen@buaa.edu.cn")
        # 获取自己的作品详情
        user_info = list(
            open_alex.get_list_of_works(filters={"author.id": open_alex_id}, pages=[pages, ], per_page=per_page))

        # 自己作品列表长度
        user_info_length = len(user_info[0]['results'])
        for i in range(user_info_length):
            # 如果没有原文
            if not user_info[0]['results'][i]['open_access'].get('oa_url', False):
                try:
                    # 说明上传了PDF,且该PDF没有删除
                    work_key, work_dic = cache_get_by_id('work', 'work',
                                                         user_info[0]['results'][i]['id'].split('/')[-1])
                    user_info[0]['results'][i]['open_access']['is_oa'] = True
                    user_info[0]['results'][i]['open_access']['oa_url'] = work_dic['url']
                except:
                    pass
        result = {'result': 1, 'message': r"获取门户信息成功！", 'user_info': user_info}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': r"请求方式错误！"}
        return JsonResponse(result)


def human_verify(request):
    # 获取表单信息
    data_json = json.loads(request.body.decode())
    # 获取到需要查询的页数以及每页多少个
    arr2 = data_json.get('arr', '[]')

    sum1 = 0
    for data in arr2:
        sum1 += data
    avg = sum1 * 1.0 / len(arr2)
    sum2 = 0.0
    for data in arr2:
        sum2 += pow(data - avg, 2)
    stddev = sum2 / len(arr2)
    if stddev != 0:
        return JsonResponse({'result': 1, 'flag': True, 'message': '真人验证通过'})
    else:
        return JsonResponse({'result': 1, 'flag': False, 'message': '真人验证失败'})
