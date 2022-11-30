import json

from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from utils.Login_utils import login_checker
from utils.Redis_utils import cache_get_list_by_diophila


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

        author_works = cache_get_list_by_diophila(request_body_json)

        # print(len(author_works[0]['results']))
        # # print(author_works[0]['results'][0])
        # print(author_works[0]['results'][0]['authorships'])
        # print(len(author_works[0]['results'][0]['authorships']))
        # print(author_works[0]['results'][0]['authorships'][0])
        cooperation_author_count = 0
        cooperation_author_list = []
        for work in author_works[0]['results']:
            work_id = work["id"].split('/')[-1]
            work_name = work["title"]
            this_work = {'work_id': work_id, 'work_name': work_name}
            author_list = work["authorships"]
            list_length = len(author_list)
            if list_length == 1:
                continue
            else:
                for author in author_list:
                    if author['author']['id'] == author_id:
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
        return JsonResponse(
            {'result': 1, 'message': '获取成功', 'cooperation_author_count': cooperation_author_count,
             'cooperation_author_list': cooperation_author_list})
