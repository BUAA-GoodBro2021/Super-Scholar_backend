"""
Redis操作相关工具类
"""
import django
import os

from django.apps import apps
from django.core.cache import cache


# 根据所属APP名, 类名和id 进行缓存并获取该实体的缓存键和信息字典
# (先看缓存是否存在, 如果不存在, 查询mysql信息并存入缓存, 返回缓存中的值)
# 该函数必须需要被try包裹
def cache_get_by_id(app_label, model_name, model_id):
    """
    :param app_label:   APP名
    :param model_name:  类名
    :param model_id:    类id
    :return:            缓存键和信息字典
    """
    # 加载所有类
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Summer.settings')
    django.setup()

    # 生成缓存键
    key = app_label + ":" + model_name + ":" + str(model_id)

    # 得到需要进行操作的类
    model = apps.get_model(app_label=app_label, model_name=model_name)

    # 获取缓存
    model_dict = cache.get(key)

    # 缓存中没有
    if model_dict is None:
        model_dict = model.objects.get(id=model_id).to_dic()
        cache.set(key, model_dict)

    return key, model_dict


# 添加某个类的所有缓存
def cache_set_all(app_label, model_name):
    # 加载所有类
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Summer.settings')
    django.setup()
    try:
        # 得到需要进行操作的类
        model = apps.get_model(app_label=app_label, model_name=model_name)
        # 获取该类的所有对象
        model_list = model.objects.all()

        for every_model in model_list:
            cache_get_by_id(app_label, model_name, every_model.id)
    except Exception:
        return 0
    return 1


# 删除某个类的所有缓存
def cache_del_all(app_label, model_name):
    # 加载所有类
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Summer.settings')
    django.setup()
    try:
        # 得到需要进行操作的类
        model = apps.get_model(app_label=app_label, model_name=model_name)
        # 获取该类的所有对象
        model_list = model.objects.all()

        for every_model in model_list:
            # 生成缓存键
            key = app_label + ":" + model_name + ":" + str(every_model.id)
            cache.delete(key)
    except Exception:
        return 0
    return 1
