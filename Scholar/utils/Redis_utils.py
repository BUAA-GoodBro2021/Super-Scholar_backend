"""
Redis操作相关工具类
"""
import json
import django
import os

from diophila import OpenAlex
from django.apps import apps
from django.core.cache import cache

# 根据所属APP名, 类名和id 进行缓存并获取该实体的缓存键和信息字典
# (先看缓存是否存在, 如果不存在, 查询mysql信息并存入缓存, 返回缓存中的值)
# 该函数必须需要被try包裹
from properties import open_alex_mailto_email


def cache_set_after_create(app_label, model_name, model_id, model_dict):
    """
        :param app_label:   APP名
        :param model_name:  类名
        :param model_id:    类id
        :param model_dict   model的信息字典
    """
    # 加载所有类
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Scholar.settings')
    django.setup()

    # 生成缓存键
    key = app_label + ":" + model_name + ":" + str(model_id)
    cache.set(key, model_dict)


def cache_get_by_id(app_label, model_name, model_id):
    """
    :param app_label:   APP名
    :param model_name:  类名
    :param model_id:    类id
    :return:            缓存键和信息字典
    """
    # 加载所有类
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Scholar.settings')
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
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Scholar.settings')
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
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Scholar.settings')
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


# 删除某个类下某个id的缓存
def cache_del_by_id(app_label, model_name, model_id):
    key = app_label + ":" + model_name + ":" + str(model_id)
    cache.delete(key)
    return 1


# 获取筛选列表
def cache_get_list_by_diophila(request_body_json):
    # 创建一个 OpenAlex 对象
    open_alex = OpenAlex(open_alex_mailto_email)
    # 处理筛选器字段，使其符合 openAlex 的筛选要求
    if request_body_json['params'].get('filter', None) is not None:
        filter_param = request_body_json['params'].get('filter', None).copy()
        # 如果筛选器字段中存在值为空字符串的键值对
        for key, value in filter_param.items():
            if value == '':
                request_body_json['params']['filter'].pop(key)
        if len(request_body_json['params']['filter']) == 0:
            request_body_json['params'].pop('filter')

    # 处理排序字段，使其符合 openAlex 的排序要求
    if request_body_json['params'].get('sort', None) is not None:
        sort_param = request_body_json['params'].get('sort', None).copy()
        # 如果排序器字段中存在值为空字符串的键值对
        for key, value in sort_param.items():
            if value == '':
                request_body_json['params']['sort'].pop(key)
        # 如果多级排序中既有升序也有降序
        if 'asc' in sort_param.values() and 'desc' in sort_param.values():
            for key, value in sort_param.items():
                if value != 'desc':
                    request_body_json['params']['sort'].pop(key)
        if len(request_body_json['params']['sort']) == 0:
            request_body_json['params'].pop('sort')
    # 生成缓存键
    key = json.dumps(request_body_json)
    # 获取查询结果
    value = cache.get(key)
    # 如果缓存中没有
    if value is None:
        if request_body_json['entity_type'] == 'works':
            value = list(open_alex.get_list_of_works(filters=request_body_json['params'].get('filter', None),
                                                     search=request_body_json['params'].get('search', None),
                                                     sort=request_body_json['params'].get('sort', None),
                                                     per_page=int(request_body_json['params'].get('per_page', 25)),
                                                     pages=[int(request_body_json['params'].get('page', 1)), ]))
            # 自己作品列表长度
            value_length = len(value[0]['results'])
            for i in range(value_length):
                if value[0]['results'][i]['abstract_inverted_index'] != None:
                    value[0]['results'][i]['abstract'] = get_work_abstract(
                        value[0]['results'][i]['abstract_inverted_index'])
                else:
                    value[0]['results'][i]['abstract'] = ""

                # 如果 openAlex 信息中没有原文
                if not value[0]['results'][i]['open_access'].get('is_oa', False):
                    try:
                        # 是否上传 PDF, 如果上传并审核成功是 1, 上传正在审核是 0, 如果没有上传是 -1
                        work_key, work_dic = cache_get_by_id('work', 'work',
                                                             value[0]['results'][i]['id'].split('/')[-1])
                        value[0]['results'][i]['open_access']['is_oa'] = work_dic['has_pdf']
                        value[0]['results'][i]['open_access']['oa_url'] = work_dic['url']
                    except:
                        value[0]['results'][i]['open_access']['is_oa'] = -1
                # 如果 openAlex 信息中有原文，状态是 1
                else:
                    value[0]['results'][i]['open_access']['is_oa'] = 1

        elif request_body_json['entity_type'] == 'authors':
            value = list(open_alex.get_list_of_authors(filters=request_body_json['params'].get('filter', None),
                                                       search=request_body_json['params'].get('search', None),
                                                       sort=request_body_json['params'].get('sort', None),
                                                       per_page=int(request_body_json['params'].get('per_page', 25)),
                                                       pages=[int(request_body_json['params'].get('page', 1)), ]))
        elif request_body_json['entity_type'] == 'venues':
            value = list(open_alex.get_list_of_venues(filters=request_body_json['params'].get('filter', None),
                                                      search=request_body_json['params'].get('search', None),
                                                      sort=request_body_json['params'].get('sort', None),
                                                      per_page=int(request_body_json['params'].get('per_page', 25)),
                                                      pages=[int(request_body_json['params'].get('page', 1)), ]))
        elif request_body_json['entity_type'] == 'institutions':
            value = list(open_alex.get_list_of_institutions(filters=request_body_json['params'].get('filter', None),
                                                            search=request_body_json['params'].get('search', None),
                                                            sort=request_body_json['params'].get('sort', None),
                                                            per_page=int(
                                                                request_body_json['params'].get('per_page', 25)),
                                                            pages=[int(request_body_json['params'].get('page', 1)), ]))
        elif request_body_json['entity_type'] == 'concepts':
            value = list(open_alex.get_list_of_concepts(filters=request_body_json['params'].get('filter', None),
                                                        search=request_body_json['params'].get('search', None),
                                                        sort=request_body_json['params'].get('sort', None),
                                                        per_page=int(request_body_json['params'].get('per_page', 25)),
                                                        pages=[int(request_body_json['params'].get('page', 1)), ]))
        cache.set(key, value)
    return value


# 获取筛选分组
def cache_get_groups_by_diophila(request_body_json):
    # 创建一个 OpenAlex 对象
    open_alex = OpenAlex(open_alex_mailto_email)
    # 处理筛选器字段，使其符合 openAlex 的筛选要求
    if request_body_json['params'].get('filter', None) is not None:
        filter_param = request_body_json['params'].get('filter', None).copy()
        # 如果筛选器字段中存在值为空字符串的键值对
        for key, value in filter_param.items():
            if value == '':
                request_body_json['params']['filter'].pop(key)
        if len(request_body_json['params']['filter']) == 0:
            request_body_json['params'].pop('filter')

    # 处理排序字段，使其符合 openAlex 的排序要求
    if request_body_json['params'].get('sort', None) is not None:
        sort_param = request_body_json['params'].get('sort', None).copy()
        # 如果排序器字段中存在值为空字符串的键值对
        for key, value in sort_param.items():
            if value == '':
                request_body_json['params']['sort'].pop(key)
        # 如果多级排序中既有升序也有降序
        if 'asc' in sort_param.values() and 'desc' in sort_param.values():
            for key, value in sort_param.items():
                if value != 'desc':
                    request_body_json['params']['sort'].pop(key)
        if len(request_body_json['params']['sort']) == 0:
            request_body_json['params'].pop('sort')
    # 生成缓存键
    key = json.dumps(request_body_json)
    # 获取查询结果
    value = cache.get(key)
    # 如果缓存中没有
    if value is None:
        if request_body_json['entity_type'] == 'works':
            value = open_alex.get_groups_of_works(filters=request_body_json['params'].get('filter', None),
                                                  search=request_body_json['params'].get('search', None),
                                                  sort=request_body_json['params'].get('sort', None),
                                                  group_by=request_body_json['params'].get('group_by', None))
            # 如果对时间进行分组，只需要得到最早年份和最晚年份
            if request_body_json['params']['group_by'] == 'publication_year':
                min_year = 0x7fffffff
                max_year = -1
                for year_dict in value['group_by']:
                    if min_year > int(year_dict['key']):
                        min_year = int(year_dict['key'])
                    if max_year < int(year_dict['key']):
                        max_year = int(year_dict['key'])
                value['meta']['min_year'] = min_year
                value['meta']['max_year'] = max_year

        elif request_body_json['entity_type'] == 'authors':
            value = open_alex.get_groups_of_authors(filters=request_body_json['params'].get('filter', None),
                                                    search=request_body_json['params'].get('search', None),
                                                    sort=request_body_json['params'].get('sort', None),
                                                    group_by=request_body_json['params'].get('group_by', None))
        elif request_body_json['entity_type'] == 'venues':
            value = open_alex.get_groups_of_venues(filters=request_body_json['params'].get('filter', None),
                                                   search=request_body_json['params'].get('search', None),
                                                   sort=request_body_json['params'].get('sort', None),
                                                   group_by=request_body_json['params'].get('group_by', None))
        elif request_body_json['entity_type'] == 'institutions':
            value = open_alex.get_groups_of_institutions(filters=request_body_json['params'].get('filter', None),
                                                         search=request_body_json['params'].get('search', None),
                                                         sort=request_body_json['params'].get('sort', None),
                                                         group_by=request_body_json['params'].get('group_by', None))
        elif request_body_json['entity_type'] == 'concepts':
            value = open_alex.get_groups_of_concepts(filters=request_body_json['params'].get('filter', None),
                                                     search=request_body_json['params'].get('search', None),
                                                     sort=request_body_json['params'].get('sort', None),
                                                     group_by=request_body_json['params'].get('group_by', None))
        # 将 unknown 的去除，同时对于key中只留ID
        unknown_location = 0
        for i in range(request_body_json['params']['group_by']):
            # 去除 unknown
            if request_body_json['params']['group_by'][i]['key'] == 'unknown':
                unknown_location = i
            # 只留 OpenAlexId
            elif request_body_json['params']['group_by'][i]['key'].find("https://"):
                request_body_json['params']['group_by'][i]['key'] = \
                    request_body_json['params']['group_by'][i]['key'].split('/')[-1]
        request_body_json['params']['group_by'].remove(unknown_location)
        cache.set(key, value)
    return value


# 根据倒排索引还原论文摘要
def get_work_abstract(abstract_inverted_index):
    abstract_table = []
    for key, value in abstract_inverted_index.items():
        value_length = len(value)
        for i in range(value_length):
            abstract_table.insert(value[i], key)

    abstract = ' '.join(abstract_table)
    return abstract


# 根据 请求体内的查询字典 进行缓存并获取查询结果
def cache_get_single_by_diophila(request_body_json):
    # 创建一个 OpenAlex 对象
    open_alex = OpenAlex(open_alex_mailto_email)
    # 生成缓存键
    key = json.dumps(request_body_json)
    # 获取查询结果
    value = cache.get(key)
    # 如果缓存中没有
    if value is None:
        if request_body_json['entity_type'] == 'works':
            # 获取论文 ID
            work_id = request_body_json['params']['id']
            # 获取论文主要信息
            value = open_alex.get_single_work(work_id)

            # 根据倒排索引获得摘要
            if value['abstract_inverted_index'] != None:
                value['abstract'] = get_work_abstract(value['abstract_inverted_index'])
            else:
                value['abstract'] = ""

            # 如果 openAlex 信息中没有原文
            if not value['open_access'].get('is_oa', False):
                try:
                    # 是否上传 PDF, 如果上传并审核成功是 1, 上传正在审核是 0, 如果没有上传是 -1
                    work_key, work_dic = cache_get_by_id('work', 'work', value['id'].split('/')[-1])
                    value['open_access']['is_oa'] = work_dic['has_pdf']
                    value['open_access']['oa_url'] = work_dic['url']
                except:
                    value['open_access']['is_oa'] = -1
            # 如果 openAlex 信息中有原文，状态是 1
            else:
                value['open_access']['is_oa'] = 1

        elif request_body_json['entity_type'] == 'authors':
            # 获取作者 ID
            author_id = request_body_json['params']['id']
            # 获取作者主要信息
            value = open_alex.get_single_author(author_id)
        elif request_body_json['entity_type'] == 'venues':
            # 获取文献来源 ID
            venue_id = request_body_json['params']['id']
            # 获取文献来源主要信息
            value = open_alex.get_single_venue(venue_id)
        elif request_body_json['entity_type'] == 'institutions':
            # 获取机构 ID
            institution_id = request_body_json['params']['id']
            # 获取机构主要信息
            value = open_alex.get_single_institution(institution_id)
        elif request_body_json['entity_type'] == 'concepts':
            # 获取概念领域 ID
            concept_id = request_body_json['params']['id']
            # 获取概念领域主要信息
            value = open_alex.get_single_concept(concept_id)
        # 进行缓存
        cache.set(key, value)
    return value
