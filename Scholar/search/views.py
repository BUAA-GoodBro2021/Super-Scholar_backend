import requests
from django.http import JsonResponse
from properties import *
from diophila import OpenAlex
from utils.Redis_utils import *


# 获取 OpenAlex 五大实体的数量
def get_open_alex_data_num():
    # 创建一个 OpenAlex 对象
    open_alex = OpenAlex(open_alex_mailto_email)
    key = "open_alex_num"
    value = cache.get(key)
    # 如果缓存中没有
    if value is None:
        work_single = next(iter(open_alex.get_list_of_works(per_page=1)))
        work_count = work_single['meta']['count']
        author_single = next(iter(open_alex.get_list_of_authors(per_page=1)))
        author_count = author_single['meta']['count']
        venues_single = next(iter(open_alex.get_list_of_venues(per_page=1)))
        venues_count = venues_single['meta']['count']
        institutions_single = next(iter(open_alex.get_list_of_institutions(per_page=1)))
        institutions_count = institutions_single['meta']['count']
        concepts_single = next(iter(open_alex.get_list_of_concepts(per_page=1)))
        concepts_count = concepts_single['meta']['count']
        value = work_count, author_count, venues_count, institutions_count, concepts_count
        cache.set(key, value)
    return value


# 获取主页信息
def get_index_data_view(request):
    if request.method == 'POST':
        # 获取引用量前25的论文
        request_body_json = {
            "entity_type": "works",
            "params": {
                "filter": {
                    "from_publication_date": "2000-01-01",
                    "to_publication_date": "2023-11-01"
                },
                "sort": {"cited_by_count": "desc"},
                "page": 1,
                "per_page": 25
            }
        }
        recommended_work_list_by_cited_count = cache_get_list_by_diophila(request_body_json)

        # 获取发布时间前25的论文
        request_body_json = {
            "entity_type": "works",
            "params": {
                "filter": {"to_publication_date": "2023-11-01"},
                "sort": {"publication_date": "desc"},
                "page": 1,
                "per_page": 25
            }
        }
        recommended_work_list_by_publication_date = cache_get_list_by_diophila(request_body_json)

        # 获取主页五大实体的数据
        work_count, author_count, venues_count, institutions_count, concepts_count = get_open_alex_data_num()
        result = {'result': 1, 'message': r"获取主页信息成功！",
                  "recommended_work_list_by_cited_count": recommended_work_list_by_cited_count,
                  "recommended_work_list_by_publication_date": recommended_work_list_by_publication_date,
                  "work_count": work_count, "author_count": author_count, "venues_count": venues_count,
                  "institutions_count": institutions_count, "concepts_count": concepts_count}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': r"请求方式错误！"}
        return JsonResponse(result)


# 联想用户搜索的内容
def associate_content_view(request):
    if request.method == 'POST':
        # 获取请求体
        request_body_json = json.loads(request.body.decode())

        # 获取查询内容
        entity_type = request_body_json['entity_type']
        params = request_body_json['params']
        # 添加认证邮箱
        params['mailto'] = open_alex_mailto_email
        response = requests.get(open_alex_base_url + "autocomplete/" + entity_type, params=params)
        return JsonResponse(response.json())
    else:
        result = {'result': 0, 'message': r"请求方式错误！"}
        return JsonResponse(result)


# 用户查看具体单个实体
def get_single_data_view(request):
    if request.method == 'POST':
        # 获取请求体
        request_body_json = json.loads(request.body.decode())

        if request_body_json['entity_type'] == 'works':
            # 获取主体
            single_data = cache_get_single_by_diophila(request_body_json)
            result = {'result': 1, 'message': r"获取论文详情成功！", "single_data": single_data}
        elif request_body_json['entity_type'] == 'authors':
            # 获取主体
            single_data = cache_get_single_by_diophila(request_body_json)
            result = {'result': 1, 'message': r"获取作者详情成功！", "single_data": single_data}
        elif request_body_json['entity_type'] == 'venues':
            # 获取主体
            single_data = cache_get_single_by_diophila(request_body_json)
            result = {'result': 1, 'message': r"获取文献来源详情成功！", "single_data": single_data}
        elif request_body_json['entity_type'] == 'institutions':
            # 获取主体
            single_data = cache_get_single_by_diophila(request_body_json)
            result = {'result': 1, 'message': r"获取机构详情成功！", "single_data": single_data}
        elif request_body_json['entity_type'] == 'concepts':
            # 获取主体
            single_data = cache_get_single_by_diophila(request_body_json)
            result = {'result': 1, 'message': r"获取概念领域详情成功！", "single_data": single_data}
        else:
            result = {'result': 0, 'message': r"请求实体类型错误，该实体类型不属于网站所包含的实体！"}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': r"请求方式错误！"}
        return JsonResponse(result)


# 用户筛选实体
def get_list_of_data_view(request):
    if request.method == 'POST':
        # 获取请求体
        request_body_json = json.loads(request.body.decode())

        if request_body_json['entity_type'] == 'works':
            # 筛选实体
            list_of_data = cache_get_list_by_diophila(request_body_json)
            result = {'result': 1, 'message': r"筛选论文成功！", "list_of_data": list_of_data}
        elif request_body_json['entity_type'] == 'authors':
            # 筛选实体
            list_of_data = cache_get_list_by_diophila(request_body_json)
            result = {'result': 1, 'message': r"筛选作者成功！", "list_of_data": list_of_data}
        elif request_body_json['entity_type'] == 'venues':
            # 筛选实体
            list_of_data = cache_get_list_by_diophila(request_body_json)
            result = {'result': 1, 'message': r"筛选文献来源成功！", "list_of_data": list_of_data}
        elif request_body_json['entity_type'] == 'institutions':
            # 筛选实体
            list_of_data = cache_get_list_by_diophila(request_body_json)
            result = {'result': 1, 'message': r"筛选机构成功！", "list_of_data": list_of_data}
        elif request_body_json['entity_type'] == 'concepts':
            # 筛选实体
            list_of_data = cache_get_list_by_diophila(request_body_json)
            result = {'result': 1, 'message': r"筛选概念领域成功！", "list_of_data": list_of_data}
        else:
            result = {'result': 0, 'message': r"请求实体类型错误，该实体类型不属于网站所包含的实体！"}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': r"请求方式错误！"}
        return JsonResponse(result)


# 用户对筛选论文进行分组
def get_groups_of_data_view(request):
    if request.method == 'POST':
        # 获取请求体
        request_body_json = json.loads(request.body.decode())
        if request_body_json['entity_type'] == 'works':
            # 分组实体
            groups_of_data = cache_get_groups_by_diophila(request_body_json)
            result = {'result': 1, 'message': r"论文分组成功！", "groups_of_data": groups_of_data}
        elif request_body_json['entity_type'] == 'authors':
            # 分组实体
            groups_of_data = cache_get_groups_by_diophila(request_body_json)
            result = {'result': 1, 'message': r"作者分组成功！", "groups_of_data": groups_of_data}
        elif request_body_json['entity_type'] == 'venues':
            # 分组实体
            groups_of_data = cache_get_groups_by_diophila(request_body_json)
            result = {'result': 1, 'message': r"文献来源分组成功！", "groups_of_data": groups_of_data}
        elif request_body_json['entity_type'] == 'institutions':
            # 分组实体
            groups_of_data = cache_get_groups_by_diophila(request_body_json)
            result = {'result': 1, 'message': r"机构分组成功！", "groups_of_data": groups_of_data}
        elif request_body_json['entity_type'] == 'concepts':
            # 分组实体
            groups_of_data = cache_get_groups_by_diophila(request_body_json)
            result = {'result': 1, 'message': r"概念领域分组成功！", "groups_of_data": groups_of_data}
        else:
            result = {'result': 0, 'message': r"请求实体类型错误，该实体类型不属于网站所包含的实体！"}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': r"请求方式错误！"}
        return JsonResponse(result)
