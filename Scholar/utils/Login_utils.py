"""
登录检测相关工具类
"""
import hashlib
import time
import jwt
import json
from django.http import JsonResponse
from properties import TOKEN_SECRET_KEY
# Hash-md5 加密字符串
from utils.Redis_utils import cache_get_by_id


def hash_encode(str_key):
    """
    :param str_key: 需要使用 md5 加密的字符串
    :return: md5 加密后的字符串
    哈希算法 - 给定明文，计算出定长的，不可逆的值
    """
    # 生成一个 md5 加密对象
    md5 = hashlib.md5()
    # 进行 md5 加密(要求加密字符串为二进制形式，需要进行encode操作)
    md5.update(str_key.encode())
    # 完成加密
    return md5.hexdigest()


# 签发登录令牌
def sign_token(payload, exp=3600 * 24):
    """
    :param payload: 私有声明字典
    :param exp: 过期时间
    :return: 签发的登录令牌
    """
    # 获取当前时间戳，并计算得到该令牌的过期时间(默认过期时间为1天)
    payload['exp'] = time.time() + exp
    # 使用 HS256 算法配合密钥签发登录令牌
    token = jwt.encode(payload, TOKEN_SECRET_KEY, algorithm='HS256')
    return token


# 校验登录令牌
def check_token(token):
    """
    :param token: 登录令牌
    :return: None - 失败(篡改,过期,为空)    payload - 成功
    """
    # 校验token
    try:
        # 查看令牌是否过期或者被篡改
        payload = jwt.decode(token, TOKEN_SECRET_KEY, algorithms=['HS256'])
    except Exception:
        # 如果失败返回 0
        return None
    # 如果成功返回1
    return payload


def login_checker(func):
    """
    :param func: 请求信息
    :return: 如果成功在request中加入token中记录的user_id，如果失败直接返回重新登陆
    """

    def wrap(request, *args, **kwargs):

        # 校验请求方式
        if request.method != 'POST':
            result = {'result': 0, 'message': '请求方式错误'}
            return JsonResponse(result)

        # 获取token
        token = request.META.get('HTTP_AUTHORIZATION')
        # print(token)
        # 校验token信息
        payload = check_token(token)
        # print(payload)
        # 校验失败
        if payload is None or payload['user_id'] <= 0:
            result = {'result': 0, 'message': '请先登录'}
            return JsonResponse(result)

        # 获取令牌中的user_id信息
        user_id = payload.get('user_id', 0)
        request.user_id = user_id

        # 加入缓存
        cache_get_by_id('user', 'user', user_id)

        return func(request, *args, **kwargs)

    return wrap


# body的token装饰器
def login_body_checker(func):
    """
    :param func: 请求信息
    :return: 如果成功在request中加入token中记录的user_id，如果失败直接返回重新登陆
    """

    def wrap(request, *args, **kwargs):

        # 校验请求方式
        if request.method != 'POST':
            result = {'result': 0, 'message': '请求方式错误'}
            return JsonResponse(result)

        try:
            token = request.META.get('HTTP_AUTHORIZATION')
            # post_body = json.loads(request.body)
            # token = post_body['token']
        except Exception:
            result = {'result': 0, 'message': '参数格式错误!'}
            return JsonResponse(result)
        # 校验token信息
        payload = check_token(token)

        # 校验失败
        if payload is None or payload['user_id'] <= 0:
            result = {'result': 0, 'message': '请先登录'}
            return JsonResponse(result)

        # 获取令牌中的user_id信息
        user_id = payload.get('user_id', 0)
        request.user_id = user_id

        # 加入缓存
        cache_get_by_id('user', 'user', user_id)

        return func(request, *args, **kwargs)

    return wrap
