import json

from django.http import JsonResponse

# Create your views here.
from form.views import open_alex
from utils.Login_utils import login_checker
from utils.Redis_utils import cache_get_list_by_diophila, get_work_abstract, cache_get_by_id


def partition(arr, low, high):
    i = (low - 1)  # 最小元素索引
    pivot = arr[high]

    for j in range(low, high):
        print(1)
        # 当前元素小于或等于 pivot
        if arr[j]['cooperation_author_count'] >= pivot['cooperation_author_count']:
            i = i + 1
            arr[i], arr[j] = arr[j], arr[i]

    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1


# arr[] --> 排序数组
# low  --> 起始索引
# high  --> 结束索引

# 快速排序函数
def quickSort(arr, low, high):
    if low < high:
        pi = partition(arr, low, high)

        quickSort(arr, low, pi - 1)
        quickSort(arr, pi + 1, high)


@login_checker
def get_relate_net(request):
    if request.method == 'POST':
        data_json = json.loads(request.body.decode())
        print(data_json)
        user_id = request.user_id
        author_id = data_json.get('author_id', '')
        request_body_json = {
            "entity_type": "works",
            "params": {
                "filter": {
                    "author.id": author_id
                },
                "page": 1,
                "per_page": 200
            }
        }
        author_works = get_value(request_body_json)
        cooperation_author_count = 0
        cooperation_author_list = []
        for work in author_works[0]['results']:
            try:
                work_id = work["id"].split('/')[-1]
                work_name = work["title"]
                this_work = {'work_id': work_id, 'work_name': work_name}
                author_list = work["authorships"]
            except:
                continue
            list_length = len(author_list)
            if list_length == 1:
                continue
            else:

                for author in author_list:

                    try:
                        if author['author']['id'].split('/')[-1] == author_id:
                            continue
                        else:
                            co_author_name = author["author"]["display_name"]
                            co_author_id = author["author"]["id"].split('/')[-1]
                            flag = False
                            for co_author in cooperation_author_list:
                                if co_author['author_id'] == co_author_id:
                                    co_author['cooperation_author_count'] = co_author['cooperation_author_count'] + 1
                                    co_author['work_list'].append(this_work)
                                    flag = True
                                    break
                            if not flag:
                                cooperation_author_count = cooperation_author_count + 1
                                co_author = {
                                    'author_name': co_author_name,
                                    'author_id': co_author_id,
                                    'cooperation_author_count': 1,
                                    'work_list': [this_work]
                                }
                                cooperation_author_list.append(co_author)
                    except:
                        print(author)
                        continue

        cooperation_author_list.sort(key=lambda s: s['cooperation_author_count'])

        return JsonResponse(
            {'result': 1, 'message': '获取成功', 'cooperation_author_count': cooperation_author_count,
             'cooperation_author_list': cooperation_author_list})


def get_value(request_body_json):
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

            # 获取 2022 的引用量
            if len(value[0]['results'][i]['counts_by_year']) == 0 or \
                    value[0]['results'][i]['counts_by_year'][0]['year'] != 2022:
                value[0]['results'][i]['2022_cited_count'] = 0
            else:
                value[0]['results'][i]['2022_cited_count'] = value[0]['results'][i]['counts_by_year'][0][
                    'cited_by_count']
        return value
