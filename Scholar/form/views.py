from form.tasks import *
from form.models import *
from utils.Redis_utils import *
from utils.Sending_utils import *
# Create your views here.
from django.core.cache import cache
from author.models import *

open_alex = OpenAlex("853048903@qq.com")


@login_checker
def user_claim_author(request):  # 用户申请认领门户
    if request.method == 'POST':
        data_json = json.loads(request.body.decode())
        print(data_json)
        content = data_json.get('content', '默认申请内容')
        user_id = request.user_id
        author_id = data_json.get('author_id', '')
        try:
            open_alex.get_single_author(author_id)
        except:
            return JsonResponse({'result': 0, 'message': '申请的作者不存在'})
        user_key, user_dic = cache_get_by_id('user', 'user', user_id)
        if user_dic["is_professional"] == 0:
            return JsonResponse({'result': 0, 'message': '用户正在申请认领门户，请放弃当前申请后再次申请'})
        if user_dic["is_professional"] == 1:
            return JsonResponse({'result': 0, 'message': '用户已经认领门户，请放弃当前门户后再次申请'})
        form_handling_key, form_handling_dic = cache_get_by_id('form', 'Form_list', 0)  # 从cache中获得正在处理的申请的id列表
        new_claim = Form.objects.create(author_id=author_id, content=content, id=user_id)
        cache_set_after_create('form', 'Form', new_claim.id, new_claim.to_dic())  # 将刚刚生成的表单放在redis中
        user_dic["is_professional"] = 0  # 表示正在申请
        user_dic["open_alex_id"] = author_id
        cache.set(user_key, user_dic)
        celery_claim_author.delay(author_id, user_id)
        form_handling_dic["Form_id_list"].append(new_claim.id)  # 拓展redis中的正在申请列表
        cache.set(form_handling_key, form_handling_dic)  # 把更新后的未处理申请id列表保存在redis中
        celery_add_form_list.delay(0, new_claim.id)  # 数据库修改
        return JsonResponse({'result': 1, 'message': '申请已经发送，请等待管理员审核'})


@login_checker
def user_give_up_author(request):  # 用户放弃申请门户或放弃当前门户
    if request.method == 'POST':
        data_json = json.loads(request.body.decode())
        print(data_json)
        user_id = request.user_id
        user_key, user_dic = cache_get_by_id('user', 'User', user_id)
        if user_dic["is_professional"] == -1:
            return JsonResponse({'result': 0, 'message': '当前用户暂无申请或无门户'})
        user_dic["is_professional"] = -1
        user_dic["open_alex_id"] = None
        cache.set(user_key, user_dic)
        if user_dic["is_professional"] == 0:
            cache.delete('form:Form:' + str(user_id))
            celery_del_form.delay(user_id)

            form_handling_key, form_handling_dic = cache_get_by_id('form', 'Form_list', 0)  # 从cache中获得正在处理的申请的id列表
            form_handling_id_list = form_handling_dic["Form_id_list"]
            form_handling_id_list.remove(user_id)
            form_handling_dic["Form_id_list"] = form_handling_id_list
            cache.set(form_handling_key, form_handling_dic)
            celery_remove_form_list.delay(0, user_id)
        return JsonResponse({'result': 1, 'message': '放弃成功'})


@login_checker
def manager_check_claim(request):  # 管理员查看未处理申请
    if request.method == 'POST':
        data_json = json.loads(request.body.decode())
        print(data_json)
        user_id = request.user_id
        super_user_key, super_user_dic = cache_get_by_id('user', 'user', user_id)
        if not super_user_dic['is_super']:
            return JsonResponse({'result': 0, 'message': '当前用户不是管理员'})
        form_handling_key, form_handling_dic = cache_get_by_id('form', 'Form_list', 0)  # 从cache中获得正在处理的申请的id列表
        form_handling_id_list = form_handling_dic["Form_id_list"]  # 取出需要的id列表
        form_handling_dic_list = []  # 初始化需要返回的字典列表
        for form_id in form_handling_id_list:
            form_key, form_dic = cache_get_by_id('form', 'form', form_id)  # 查找form
            form_handling_dic_list.append(form_dic)
        return JsonResponse({'result': 1, 'message': '查询未处理申请完毕', 'form_handling_dic_list': form_handling_dic_list})


@login_checker
def manager_deal_claim(request):  # 管理员处理未处理申请
    if request.method == 'POST':
        data_json = json.loads(request.body.decode())
        print(data_json)
        user_id = request.user_id
        deal_result = int(data_json.get('deal_result', 2))

        form_handling_key, form_handling_dic = cache_get_by_id('form', 'Form_list', 0)  # 从cache中获得正在处理的申请的id列表
        form_handling_id_list = form_handling_dic["Form_id_list"]
        form_handling_id_list.remove(user_id)
        form_handling_dic["Form_id_list"] = form_handling_id_list
        cache.set(form_handling_key, form_handling_dic)
        celery_remove_form_list.delay(0, user_id)

        # form_list_key, form_list_dic = cache_get_by_id('form', 'Form_list', deal_result)
        # form_id_list = form_list_dic["Form_id_list"]
        # form_id_list.append(user_id)
        # form_list_dic["Form_id_list"] = form_id_list
        # cache.set(form_list_key, form_list_dic)
        # celery_add_form_list.delay(deal_result, user_id)

        cache.delete('form:' + 'Form:' + str(user_id))
        # form_key, form_dic = cache_get_by_id('form', 'Form', user_id)
        # form_dic["is_pass"] = deal_result
        # cache.set(form_key, form_dic)
        celery_del_form.delay(user_id)

        user_key, user_dic = cache_get_by_id('user', 'User', user_id)
        if deal_result == 1:
            user_dic["is_professional"] = 1
        else:
            user_dic["is_professional"] = -1
            user_dic["open_alex_id"] = None
        cache.set(user_key, user_dic)
        celery_change_user_pass.delay(deal_result, user_id)

        # if deal_result == 1:
        #     user_key, user_dic = cache_get_by_id('user', 'user', user_id)
        #     user_dic["is_professional"] = True
        #     cache.set(user_key, user_dic)
        #     celery_change_user_pass(user_id)

        return JsonResponse({'result': 1, 'message': '处理成功'})
