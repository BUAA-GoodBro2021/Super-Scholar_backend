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
                    "from_publication_date": "2002-01-01",
                    "to_publication_date": "2022-12-13"
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
                "filter": {"to_publication_date": "2022-12-13"},
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


def get_open_alex_data_num_view(request):
    # 获取主页五大实体的数据
    work_count, author_count, venues_count, institutions_count, concepts_count = get_open_alex_data_num()
    result = {'result': 1, 'message': r"获取数据量成功！",
              "work_count": work_count, "author_count": author_count, "venues_count": venues_count,
              "institutions_count": institutions_count, "concepts_count": concepts_count}
    return JsonResponse(result)


def get_recommended_data_view(request):
    if request.method == 'POST':
        # 获取引用量前25的论文
        request_body_json = {
            "entity_type": "works",
            "params": {
                "filter": {
                    "from_publication_date": "2002-01-01",
                    "to_publication_date": "2022-12-13"
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
                "filter": {"to_publication_date": "2022-12-13"},
                "sort": {"publication_date": "desc"},
                "page": 1,
                "per_page": 25
            }
        }
        recommended_work_list_by_publication_date = cache_get_list_by_diophila(request_body_json)

        result = {'result': 1, 'message': r"获取推荐信息成功！",
                  "recommended_work_list_by_cited_count": recommended_work_list_by_cited_count,
                  "recommended_work_list_by_publication_date": recommended_work_list_by_publication_date}
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
        return JsonResponse({'result': 1, 'message': r"联想成功", 'associate_content': response.json()})
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


# 高级检索
def advanced_search_view(request):
    if request.method == 'POST':
        # 获取请求体
        request_body_json = json.loads(request.body.decode())
        url = "https://api.openalex.org/" + request_body_json['entity_type']

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

        filter_dict = request_body_json['params'].get('filter', None)
        search_string = request_body_json['params'].get('search', None)
        sort_dict = request_body_json['params'].get('sort', None)

        page = str(request_body_json['params'].get('page', 1))
        per_page = str(request_body_json['params'].get('per_page', 25))

        if request_body_json['entity_type'] == 'works':
            # 如果需要查询某个作者
            if filter_dict.get("authorships.author.display_name", None) is not None:
                author_list = []
                display_name_string = filter_dict['authorships.author.display_name']
                display_name_string = display_name_string.replace("|", "&")
                display_name_list = display_name_string.split("&")
                for every_display_name in display_name_list:
                    if every_display_name[0] != "!":
                        value = cache_get_list_by_diophila(
                            {
                                "entity_type": "authors",
                                "params": {
                                    "search": every_display_name,
                                    "page": 1,
                                    "per_page": 5
                                }
                            }
                        )
                        for every_author in value[0]['results']:
                            author_list.append(every_author['id'].split('/')[-1])
                filter_dict['authorships.author.id'] = '|'.join(author_list)
                filter_dict.pop("authorships.author.display_name")

            # 如果需要查询某个机构
            if filter_dict.get("authorships.institutions.display_name", None) is not None:
                institution_list = []
                display_name_string = filter_dict['authorships.institutions.display_name']
                display_name_string = display_name_string.replace("|", "&")
                display_name_list = display_name_string.split("&")
                for every_display_name in display_name_list:
                    if every_display_name[0] != "!":
                        value = cache_get_list_by_diophila(
                            {
                                "entity_type": "institutions",
                                "params": {
                                    "search": every_display_name,
                                    "page": 1,
                                    "per_page": 5
                                }
                            }
                        )
                        for every_institution in value[0]['results']:
                            institution_list.append(every_institution['id'].split('/')[-1])
                filter_dict['authorships.institutions.id'] = '|'.join(institution_list)
                filter_dict.pop("authorships.institutions.display_name")

            # 如果需要查询某个期刊会议
            if filter_dict.get("host_venue.display_name", None) is not None:
                venue_list = []
                display_name_string = filter_dict['host_venue.display_name']
                display_name_string = display_name_string.replace("|", "&")
                display_name_list = display_name_string.split("&")
                for every_display_name in display_name_list:
                    if every_display_name[0] != "!":
                        value = cache_get_list_by_diophila(
                            {
                                "entity_type": "venues",
                                "params": {
                                    "search": every_display_name,
                                    "page": 1,
                                    "per_page": 5
                                }
                            }
                        )
                        for every_venue in value[0]['results']:
                            venue_list.append(every_venue['id'].split('/')[-1])
                filter_dict['host_venue.id'] = '|'.join(venue_list)
                filter_dict.pop("host_venue.display_name")

            # 如果需要查询某个期刊会议
            if filter_dict.get("concepts.display_name", None) is not None:
                concept_list = []
                display_name_string = filter_dict['concepts.display_name']
                display_name_string = display_name_string.replace("|", "&")
                display_name_list = display_name_string.split("&")
                for every_display_name in display_name_list:
                    if every_display_name[0] != "!":
                        value = cache_get_list_by_diophila(
                            {
                                "entity_type": "concepts",
                                "params": {
                                    "search": every_display_name,
                                    "page": 1,
                                    "per_page": 5
                                }
                            }
                        )
                        for every_concept in value[0]['results']:
                            concept_list.append(every_concept['id'].split('/')[-1])
                filter_dict['concepts.id'] = '|'.join(concept_list)
                filter_dict.pop("concepts.display_name")

        if request_body_json['entity_type'] == 'authors':
            # 如果需要查询某个机构
            if filter_dict.get("last_known_institution.display_name", None) is not None:
                institution_list = []
                display_name_string = filter_dict['last_known_institution.display_name']
                display_name_string = display_name_string.replace("|", "&")
                display_name_list = display_name_string.split("&")
                for every_display_name in display_name_list:
                    if every_display_name[0] != "!":
                        value = cache_get_list_by_diophila(
                            {
                                "entity_type": "institutions",
                                "params": {
                                    "search": every_display_name,
                                    "page": 1,
                                    "per_page": 5
                                }
                            }
                        )
                        for every_institution in value[0]['results']:
                            institution_list.append(every_institution['id'].split('/')[-1])
                filter_dict['last_known_institution.id'] = '|'.join(institution_list)
                filter_dict.pop("last_known_institution.display_name")

        if request_body_json['entity_type'] == 'authors' or request_body_json['entity_type'] == 'venues' or \
                request_body_json['entity_type'] == 'institutions':
            # 如果需要查询某个期刊会议
            if filter_dict.get("x_concepts.display_name", None) is not None:
                concept_list = []
                display_name_string = filter_dict['x_concepts.display_name']
                display_name_string = display_name_string.replace("|", "&")
                display_name_list = display_name_string.split("&")
                for every_display_name in display_name_list:
                    if every_display_name[0] != "!":
                        value = cache_get_list_by_diophila(
                            {
                                "entity_type": "concepts",
                                "params": {
                                    "search": every_display_name,
                                    "page": 1,
                                    "per_page": 5
                                }
                            }
                        )
                        for every_concept in value[0]['results']:
                            concept_list.append(every_concept['id'].split('/')[-1])
                filter_dict['x_concepts.id'] = '|'.join(concept_list)
                filter_dict.pop("x_concepts.display_name")

        if request_body_json['entity_type'] == 'concepts':
            # 如果需要查询某个期刊会议
            if filter_dict.get("ancestors.display_name", None) is not None:
                concept_list = []
                display_name_string = filter_dict['ancestors.display_name']
                display_name_string = display_name_string.replace("|", "&")
                display_name_list = display_name_string.split("&")
                for every_display_name in display_name_list:
                    if every_display_name[0] != "!":
                        value = cache_get_list_by_diophila(
                            {
                                "entity_type": "concepts",
                                "params": {
                                    "search": every_display_name,
                                    "page": 1,
                                    "per_page": 5
                                }
                            }
                        )
                        for every_concept in value[0]['results']:
                            concept_list.append(every_concept['id'].split('/')[-1])
                filter_dict['ancestors.id'] = '|'.join(concept_list)
                filter_dict.pop("ancestors.display_name")

        # 有过滤器
        filter_string_list = []
        if filter_dict is not None:
            url += "?filter="
            for key, value in filter_dict.items():
                # 说明没有 和&
                if value.find('&') == -1:
                    # 说明没有 或| 此时可以直接拼接
                    if value.find('|') == -1:
                        filter_string_list.append(key + ":" + value)
                    # 如果有或
                    else:
                        # 此时要筛选出带有 !非的 单独
                        or_not_list = value.split('|')
                        not_count = value.count('!')
                        # 非的个数为1才有效
                        if not_count == 0:
                            filter_string_list.append(key + ":" + value)
                        elif not_count == 1:
                            or_string_list = []
                            not_string = ""
                            for item in or_not_list:
                                if item[0] != '!':
                                    or_string_list.append(item)
                                else:
                                    not_string = item
                            filter_string_list.append(key + ":" + not_string + "|" + "|".join(or_string_list))
                        else:
                            pass
                else:
                    and_list = value.split('&')
                    url_and_string = []
                    for every_and_list in and_list:
                        # 说明没有 或| 此时可以直接拼接
                        if every_and_list.find('|') == -1:
                            url_and_string.append(key + ":" + every_and_list)
                        # 如果有或
                        else:
                            # 此时要筛选出带有 !非的 单独
                            or_not_list = every_and_list.split('|')
                            not_count = every_and_list.count('!')
                            # 非的个数为1才有效
                            if not_count == 0:
                                url_and_string.append(key + ":" + every_and_list)
                            elif not_count == 1:
                                or_string_list = []
                                not_string = ""
                                for item in or_not_list:
                                    if item[0] != '!':
                                        or_string_list.append(item)
                                    else:
                                        not_string = item
                                url_and_string.append(key + ":" + not_string + "|" + "|".join(or_string_list))
                            else:
                                pass
                    filter_string_list.append(",".join(url_and_string))

            url += ",".join(filter_string_list)
            if url[-1] == '=':
                url = url.replace("?filter=", "")

        if search_string is not None:
            url += "&search=" + search_string
            if url[-1] == '=':
                url = url.replace("&search=", "")

        if sort_dict is not None:
            url += "&sort="
            sort_string_list = []
            for key, value in sort_dict.items():
                sort_string_list.append(key + ":" + value)
            url += ",".join(sort_string_list)
            if url[-1] == '=':
                url = url.replace("&sort=", "")

        url += "&page=" + page + "&per-page=" + per_page + "&mailto=" + open_alex_mailto_email

        value = []
        data = requests.get(url).json()
        value.append(data)

        if request_body_json['entity_type'] == 'works':
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

                # 获取 2022 的引用量
                if len(value[0]['results'][i]['counts_by_year']) == 0 or \
                        value[0]['results'][i]['counts_by_year'][0]['year'] != 2022:
                    value[0]['results'][i]['2022_cited_count'] = 0
                else:
                    value[0]['results'][i]['2022_cited_count'] = value[0]['results'][i]['counts_by_year'][0][
                        'cited_by_count']

        value[0]['meta']['url'] = url
        result = {'result': 1, 'message': r"高级检索成功！", "advanced_search_data": value}
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': r"请求方式错误！"}
        return JsonResponse(result)
