from diophila import OpenAlex
from django.core.cache import cache

from history.models import History
from user.models import *
from django.http import HttpResponse
from user.tasks import *
from utils.Redis_utils import cache_set_after_create, get_work_abstract

from utils.Sending_utils import *


def test(request):
    return HttpResponse("Hello world!")


def check_number(password):
    for c in password:
        if c.isnumeric():
            return True


def check_letter(password):
    for c in password:
        if 'a' <= c <= 'z' or 'A' <= c <= 'Z':
            return True


def check_mark(password):
    for c in password:
        if not (c.isnumeric() or 'a' <= c <= 'z' or 'A' <= c <= 'Z'):
            return True


def check_legal(password):
    if len(password) < 8 or len(password) > 16:
        return {'result': 0, 'message': '长度需为8-16个字符,请重新输入。'}
    else:
        for i in password:
            if 0x4e00 <= ord(i) <= 0x9fa5 or ord(i) == 0x20:  # Ox4e00等十六进制数分别为中文字符和空格的Unicode编码
                return {'result': 0, 'message': '不能使用空格、中文，请重新输入。'}
        else:
            key = 0
            key += 1 if check_number(password) else 0
            key += 1 if check_letter(password) else 0
            key += 1 if check_mark(password) else 0
            if key >= 2:
                return {'result': 1, 'message': '密码强度合适'}
            else:
                return {'result': 0, 'message': '至少含数字/字母/字符2种组合，请重新输入。'}


# 用户注册
# TODO 密码强度检测。
def register(request):
    """
    :param request: 请求体
    :return:        1 - 成功， 0 - 失败

    请求体包含包含 username，password1，password2，email
    """
    if request.method == 'POST':

        result = {'result': 0, 'message': r"正在内测中, 暂时不对外开放注册！"}

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
            result = {'result': 0, 'message': r'该用户名已存在!'}
            return JsonResponse(result)

        # if User.objects.filter(email=email, is_active=True).exists():
        #     result = {'result': 0, 'message': r'该邮箱已存在!'}
        #     return JsonResponse(result)

        if password1 != password2:
            result = {'result': 0, 'message': r'两次密码不一致!'}
            return JsonResponse(result)

        message = check_legal(password1)

        if message['result'] != 1:
            return JsonResponse(message)

        user = User.objects.create(username=username, email=email, password=hash_encode(password1), is_active=False)

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
        token = sign_token(payload, exp=3600 * 24 * 2)

        # 获取缓存信息
        user_key, user_dict = cache_get_by_id('user', 'user', user.id)

        # 获取用户的历史记录
        if History.objects.filter(id=user.id).exists():
            history_key, history_dict = cache_get_by_id('history', 'history', user.id)
            result = {'result': 1, 'message': r"登录成功！", 'token': token, 'user': user_dict,
                      "history_list": history_dict['history_list']}
            return JsonResponse(result)
        else:
            history = History.objects.create(id=user.id)
            cache_set_after_create('history', 'history', history.id, history.to_dic())
            result = {'result': 1, 'message': r"登录成功！", 'token': token, 'user': user_dict,
                      "history_list": []}
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
        email = data_json.get('email', '')
        username = data_json.get('username', '')
        password1 = data_json.get('password1', '')
        password2 = data_json.get('password2', '')

        # 检测异常情况
        if not User.objects.filter(username=username).exists():
            result = {'result': 0, 'message': r'用户不存在!'}
            return JsonResponse(result)

        if not User.objects.filter(email=email).exists():
            result = {'result': 0, 'message': r'用户不存在!'}
            return JsonResponse(result)

        if len(password1) == 0 or len(password2) == 0:
            result = {'result': 0, 'message': r'用户名或密码不允许为空!'}
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
        username = data_json.get('name', '')
        introduction = data_json.get('introduction', 'Leave something to help others get to know you better!')

        # 异常情况
        if len(username) == 0:
            result = {'result': 0, 'message': r"用户名的长度不能为0！"}
            return JsonResponse(result)

        # 获取信息
        user_key, user_dict = cache_get_by_id('user', 'user', user_id)

        if User.objects.filter(username=username, is_active=True).exists() and user_dict['username'] != username:
            result = {'result': 0, 'message': r'用户已存在!'}
            return JsonResponse(result)

        # 修改信息，同步缓存
        user_dict['username'] = username
        user_dict['introduction'] = introduction
        cache.set(user_key, user_dict)

        # 修改数据库
        celery_change_introduction.delay(user_id, introduction, username)

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

            if user_info[0]['results'][i]['abstract_inverted_index'] != None:
                user_info[0]['results'][i]['abstract'] = get_work_abstract(
                    user_info[0]['results'][i]['abstract_inverted_index'])
            else:
                user_info[0]['results'][i]['abstract'] = ""

            # 如果 openAlex 信息中没有原文
            if not user_info[0]['results'][i]['open_access'].get('is_oa', False):
                try:
                    # 是否上传 PDF, 如果上传并审核成功是 1, 上传正在审核是 0, 如果没有上传是 -1
                    work_key, work_dic = cache_get_by_id('work', 'work',
                                                         user_info[0]['results'][i]['id'].split('/')[-1])
                    user_info[0]['results'][i]['open_access']['is_oa'] = work_dic['has_pdf']
                    user_info[0]['results'][i]['open_access']['oa_url'] = work_dic['url']
                except:
                    user_info[0]['results'][i]['open_access']['is_oa'] = -1
            # 如果 openAlex 信息中有原文，状态是 1
            else:
                user_info[0]['results'][i]['open_access']['is_oa'] = 1

            # 获取 2022 的引用量
            if len(user_info[0]['results'][i]['counts_by_year']) == 0 or \
                    user_info[0]['results'][i]['counts_by_year'][0]['year'] != 2022:
                user_info[0]['results'][i]['2022_cited_count'] = 0
            else:
                user_info[0]['results'][i]['2022_cited_count'] = user_info[0]['results'][i]['counts_by_year'][0][
                    'cited_by_count']

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
