"""
登录检测相关工具类
"""
import hashlib
import json
import time
import jwt
from django.http import JsonResponse

from properties import TOKEN_SECRET_KEY

# Hash-md5 加密字符串
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

