import requests
from django.http import JsonResponse
from properties import *

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
    if request.method == 'GET':
        # 获取引用量前25的论文
        request_body_json = {
            "entity_type": "works",
            "params": {
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
    if request.method == 'GET':
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


# 用户查看具体单篇论文
def get_single_work_data_view(request):
    if request.method == 'GET':
        # 获取请求体
        request_body_json = json.loads(request.body.decode())

        # 获取到论文主体
        work_body = cache_get_single_by_diophila(request_body_json)
        result = {'result': 1, 'message': r"获取论文详情成功！", "work_body": work_body}

        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': r"请求方式错误！"}
        return JsonResponse(result)


# 用户筛选论文
def get_list_of_works_data_view(request):
    if request.method == 'GET':
        # 获取请求体
        request_body_json = json.loads(request.body.decode())
        # 筛选论文
        list_of_works = cache_get_list_by_diophila(request_body_json)
        result = {'result': 1, 'message': r"筛选论文成功！", "list_of_works": list_of_works}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': r"请求方式错误！"}
        return JsonResponse(result)
