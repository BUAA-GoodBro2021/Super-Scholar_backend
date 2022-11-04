from form.tasks import *
from form import models
from utils.Redis_utils import *
from utils.Sending_utils import *
# Create your views here.
from django.core.cache import cache
from author import models

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
        form_handling_key, form_handling_dic = cache_get_by_id('form', 'Form_list', 0)  # 从cache中获得正在处理的申请的id列表
        new_claim = models.Form.objects.create(author_id=author_id, content=content, user_id=user_id)
        cache_set_after_create('form', 'Form', new_claim.id, new_claim.to_dic())  # 将刚刚生成的表单放在redis中
        new_author = models.Author.objects.create(open_alex_id=author_id, id=user_id)
        cache_set_after_create('author', "Author", new_author.id, new_author.to_dic())
        form_handling_dic["Form_id_list"].append(new_claim.id)  # 拓展redis中的正在申请列表
        cache.set(form_handling_key, form_handling_dic)  # 把更新后的未处理申请id列表保存在redis中
        celery_add_form_list.delay(0, new_claim.id)  # 数据库修改
        return JsonResponse({'result': 1, 'message': '申请已经发送，请等待管理员审核'})


@login_checker
def manager_check_claim(request):  # 管理员查看未处理申请
    if request.method == 'POST':
        data_json = json.loads(request.body.decode())
        print(data_json)
        user_id = request.user_id
        super_user_key, super_user_dic = cache_get_by_id('user', 'user', user_id)
        if not super_user_dic['is_super']:
            return JsonResponse({'result': 0, 'message': '申请的作者不存在'})
        form_handling_key, form_handling_dic = cache_get_by_id('form', 'Form_list', 0)  # 从cache中获得正在处理的申请的id列表
        form_handling_id_list = form_handling_dic["Form_id_list"]  # 取出需要的id列表
        form_handling_dic_list = []  # 初始化需要返回的字典列表
        for form_id in form_handling_id_list:
            form_key, form_dic = cache_get_by_id('form', 'form', form_id)  # 查找form
            form_handling_dic_list.append(form_dic)
        return JsonResponse({'result': 1, 'message': '查询未处理申请完毕', 'form_handling_dic_list': form_handling_dic_list})
