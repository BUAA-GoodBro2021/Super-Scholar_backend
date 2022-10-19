import time

import requests
from diophila import OpenAlex
from django.core.cache import cache
from django.http import JsonResponse

# 创建一个 OpenAlex 对象
open_alex = OpenAlex("zhouenshen@buaa.edu.cn")


# 获取 OpenAlex 五大实体的数量
def get_open_alex_num():
    work_single = next(iter(open_alex.get_list_of_works(per_page=1, pages=[1, ])))
    work_count = work_single['meta']['count']
    author_single = next(iter(open_alex.get_list_of_authors(per_page=1)))
    author_count = author_single['meta']['count']
    venues_single = next(iter(open_alex.get_list_of_venues(per_page=1)))
    venues_count = venues_single['meta']['count']
    institutions_single = next(iter(open_alex.get_list_of_institutions(per_page=1)))
    institutions_count = institutions_single['meta']['count']
    concepts_single = next(iter(open_alex.get_list_of_concepts(per_page=1)))
    concepts_count = concepts_single['meta']['count']

    return work_count, author_count, venues_count, institutions_count, concepts_count


# 获取主页信息
def get_index_data(work_per_page=25):
    # 获取推荐的论文列表
    recommended_work_list_by_cited_count = list(
        open_alex.get_list_of_works(sort={"cited_by_count": "desc", }, per_page=work_per_page, pages=[1, ]))
    # 获取最新论文
    recommended_work_list_by_publication_date = list(
        open_alex.get_list_of_works(sort={"publication_date": "desc", }, per_page=work_per_page, pages=[1, ]))
    return recommended_work_list_by_cited_count, recommended_work_list_by_publication_date


# # 获取主页信息
def get_index_data_view(request):
    if request.method == 'GET':

        # 生成缓存键
        key = "work?sort:desc|work?publication_date:desc"
        value = cache.get(key)
        # 缓存中没有
        if value is None:
            value = get_index_data(work_per_page=25)
            cache.set(key, value)
        recommended_work_list_by_cited_count, recommended_work_list_by_publication_date = value

        result = {'result': 1, 'message': r"获取主页信息成功！",
                  "recommended_work_list_by_cited_count": recommended_work_list_by_cited_count,
                  "recommended_work_list_by_publication_date": recommended_work_list_by_publication_date, }
        return JsonResponse(result)
    else:
        result = {'result': 0, 'message': r"请求方式错误！"}
        return JsonResponse(result)


# t1 = time.time()
# print(get_index_data())
# t2 = time.time()
# print(t2 - t1)
params = {
    "mailto": "zhouenshen@buaa.edu.cn",
    # "q": "StyTr2",
    "search": "Denoising Diffusion",
}
url = "https://api.openalex.org/" + "works"
response = requests.get(url, params=params)
print(response.json())
