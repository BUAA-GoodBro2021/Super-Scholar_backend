from django.utils.timezone import now

from form.tasks import *
from form.models import *
from utils.Redis_utils import *
from utils.Sending_utils import *
from django.core.cache import cache
from message.models import *
from author.models import *

open_alex = OpenAlex("853048903@qq.com")


@login_checker
def user_claim_author(request):  # 用户申请认领门户
    if request.method == 'POST':
        data_json = json.loads(request.body.decode())
        print(data_json)
        institution = data_json.get('institution', '机构')
        real_name = data_json.get('real_name', '真名')
        content = data_json.get('content', '默认申请内容')
        user_id = request.user_id
        author_id = data_json.get('author_id', '')
        print(author_id)
        try:
            open_alex.get_single_author(author_id)
        except:
            return JsonResponse({'result': 0, 'message': '申请的作者不存在'})
        user_key, user_dic = cache_get_by_id('user', 'user', user_id)
        print(user_dic)
        if user_dic["is_professional"] == 0:
            return JsonResponse({'result': 0, 'message': '用户正在申请认领门户，请放弃当前申请后再次申请'})
        if user_dic["is_professional"] == 1:
            return JsonResponse({'result': 0, 'message': '用户已经认领门户，请放弃当前门户后再次申请'})
        form_handling_key, form_handling_dic = cache_get_by_id('form', 'formlist', 0)  # 从cache中获得正在处理的申请的id列表
        flag = 0
        try:
            cache_get_by_id('author', 'author', author_id)
        except:
            flag = 1
        if flag == 0:
            return JsonResponse({'result': 0, 'message': '这个作者已经被认领门户'})
        try:
            new_claim = Form.objects.create(author_id=author_id, content=content, id=user_id, institution=institution,
                                            real_name=real_name, claim_time=now())
        except:
            return JsonResponse({'result': 0, 'message': '用户正在申请认领门户，请放弃当前申请后再次申请'})

        cache_set_after_create('form', 'form', new_claim.id, new_claim.to_dic())  # 将刚刚生成的表单放在redis中
        user_dic["is_professional"] = 0  # 表示正在申请
        user_dic["open_alex_id"] = author_id
        user_dic["real_name"] = real_name
        cache.set(user_key, user_dic)
        celery_claim_author.delay(author_id, user_id, real_name)
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
        try:
            user_key, user_dic = cache_get_by_id('user', 'user', user_id)
        except:
            return JsonResponse({'result': 0, 'message': '当前用户不存在'})
        if user_dic["is_professional"] == -1:
            return JsonResponse({'result': 0, 'message': '当前用户暂无申请或无门户'})

        if user_dic["is_professional"] == 0:
            cache.delete('form:form:' + str(user_id))
            celery_del_form.delay(user_id)

            form_handling_key, form_handling_dic = cache_get_by_id('form', 'formlist', 0)  # 从cache中获得正在处理的申请的id列表
            form_handling_id_list = form_handling_dic["Form_id_list"]
            form_handling_id_list.remove(user_id)
            form_handling_dic["Form_id_list"] = form_handling_id_list
            cache.set(form_handling_key, form_handling_dic)
            celery_remove_form_list.delay(0, user_id)
        if user_dic["is_professional"] == 1:
            cache.delete('author:' + 'author:' + user_dic["open_alex_id"])
            celery_delete_author.delay(user_dic["open_alex_id"])
        user_dic["is_professional"] = -1
        user_dic["open_alex_id"] = None
        user_dic['real_name'] = None
        user_dic['work_count'] = 0
        user_dic['institution'] = None
        user_dic['institution_id'] = None
        print(user_dic)
        cache.set(user_key, user_dic)
        celery_change_user_pass.delay(-1, user_id)
        return JsonResponse({'result': 1, 'message': '放弃成功'})


@login_checker
def manager_check_claim(request):  # 管理员查看未处理申请
    if request.method == 'POST':
        data_json = json.loads(request.body.decode())
        print(data_json)
        user_id = request.user_id
        try:
            super_user_key, super_user_dic = cache_get_by_id('user', 'user', user_id)
        except:
            return JsonResponse({'result': 0, 'message': '当前用户不存在'})
        if not super_user_dic['is_super']:
            return JsonResponse({'result': 0, 'message': '当前用户不是管理员'})
        try:
            form_handling_key, form_handling_dic = cache_get_by_id('form', 'formlist', 0)  # 从cache中获得正在处理的申请的id列表
        except:
            return JsonResponse({'result': 0, 'message': '当前表单列表不存在'})
        form_handling_id_list = form_handling_dic["Form_id_list"]  # 取出需要的id列表
        form_handling_dic_list = []  # 初始化需要返回的字典列表
        for form_id in form_handling_id_list:
            try:
                form_key, form_dic = cache_get_by_id('form', 'form', form_id)  # 查找form
            except:
                return JsonResponse({'result': 0, 'message': '当前表单不存在'})
            form_handling_dic_list.append(form_dic)
        return JsonResponse({'result': 1, 'message': '查询未处理申请完毕', 'form_handling_dic_list': form_handling_dic_list})


@login_checker
def manager_deal_claim(request):  # 管理员处理未处理申请
    if request.method == 'POST':
        data_json = json.loads(request.body.decode())
        print(data_json)
        user_id = request.user_id
        try:
            super_user_key, super_user_dic = cache_get_by_id('user', 'user', user_id)
        except:
            return JsonResponse({'result': 0, 'message': '当前用户不存在'})
        if not super_user_dic['is_super']:
            return JsonResponse({'result': 0, 'message': '当前用户不是管理员'})

        deal_result = int(data_json.get('deal_result', 2))
        user_id = int(data_json.get('user_id'))
        form_key, form_dic = cache_get_by_id('form', 'form', user_id)
        if deal_result == 1:
            flag = 0
            try:
                cache_get_by_id('author', 'author', form_dic["author_id"])
            except:
                flag = 1
            if flag == 0:
                return JsonResponse({'result': 0, 'message': '这个作者已经被认领门户'})

        form_handling_key, form_handling_dic = cache_get_by_id('form', 'formlist', 0)  # 从cache中获得正在处理的申请的id列表
        form_handling_id_list = form_handling_dic["Form_id_list"]
        try:
            form_handling_id_list.remove(user_id)
        except:
            return JsonResponse({'result': 0, 'message': '此用户没有申请'})
        form_handling_dic["Form_id_list"] = form_handling_id_list
        cache.set(form_handling_key, form_handling_dic)
        celery_remove_form_list.delay(0, user_id)
        cache.delete('form:' + 'form:' + str(user_id))
        celery_del_form.delay(user_id)

        try:
            user_key, user_dic = cache_get_by_id('user', 'user', user_id)
        except:
            return JsonResponse({'result': 0, 'message': '该申请用户不存在'})
        if deal_result == 1:

            user_dic["is_professional"] = 1
            user_dic['unread_message_count'] = user_dic['unread_message_count'] + 1

            author_id = form_dic["author_id"]
            author_information = open_alex.get_single_author(author_id)

            user_dic['work_count'] = author_information['works_count']
            user_dic['institution'] = author_information['last_known_institution']['display_name']
            user_dic['institution_id'] = author_information['last_known_institution']['id'].split('/')[-1]
            user_dic['real_name'] = author_information['display_name']

            this_message = Message.objects.create(send_id=0, receiver_id=user_id, message_type=1,
                                                  author_id=form_dic['author_id'], real_name=form_dic['real_name'],
                                                  institution=form_dic['institution'])
            cache_set_after_create('message', 'message', this_message.id, this_message.to_dic())
            message_id_list_key, message_id_list_dic = cache_get_by_id('message', 'usermessageidlist', user_id)
            message_id_list_dic['message_id_list'].append(this_message.id)
            cache.set(message_id_list_key, message_id_list_dic)
            celery_add_user_message_id_list.delay(user_id, this_message.id)
            this_author = Author.objects.create(id=form_dic["author_id"])
            cache_set_after_create('author', 'author', this_author.id, this_author.to_dic())
            celery_user_pass_and_add_unread_message_count.delay(user_id, user_dic)
        else:
            user_dic["is_professional"] = -1
            user_dic["open_alex_id"] = None
            user_dic['real_name'] = None
            user_dic['work_count'] = 0
            user_dic['institution'] = None
            user_dic['institution_id'] = None

            user_dic['unread_message_count'] = user_dic['unread_message_count'] + 1
            this_message = Message.objects.create(send_id=0, receiver_id=user_id, message_type=0,
                                                  author_id=form_dic['author_id'], real_name=form_dic['real_name'],
                                                  institution=form_dic['institution'])
            cache_set_after_create('message', 'message', this_message.id, this_message.to_dic())
            message_id_list_key, message_id_list_dic = cache_get_by_id('message', 'usermessageidlist', user_id)
            message_id_list_dic['message_id_list'].append(this_message.id)
            cache.set(message_id_list_key, message_id_list_dic)
            celery_add_user_message_id_list.delay(user_id, this_message.id)
            celery_change_user_pass_and_add_unread_message_count.delay(deal_result, user_id)
        cache.set(user_key, user_dic)

        return JsonResponse({'result': 1, 'message': '处理成功'})


@login_checker
def manager_look_all_user(request):
    data_json = json.loads(request.body.decode())
    print(data_json)
    user_id = request.user_id
    try:
        super_user_key, super_user_dic = cache_get_by_id('user', 'user', user_id)
    except:
        return JsonResponse({'result': 0, 'message': '当前用户不存在'})
    if not super_user_dic['is_super']:
        return JsonResponse({'result': 0, 'message': '当前用户不是管理员'})
    user_id_list_key, user_id_list_dic = cache_get_by_id('user', 'userlist', 0)
    user_dic_list = []
    for user_id in user_id_list_dic['id_list']:
        try:
            user_key, user_dic = cache_get_by_id('user', 'user', user_id)
        except:
            continue
        user_dic_list.append(user_dic)
    return JsonResponse({'result': 1, 'message': '获得所有用户成功', 'user_list': user_dic_list})


@login_checker
def manager_delete_user_author(request):
    data_json = json.loads(request.body.decode())
    print(data_json)
    user_id = request.user_id
    try:
        super_user_key, super_user_dic = cache_get_by_id('user', 'user', user_id)
    except:
        return JsonResponse({'result': 0, 'message': '当前用户不存在'})
    if not super_user_dic['is_super']:
        return JsonResponse({'result': 0, 'message': '当前用户不是管理员'})
    user_id = int(data_json.get('user_id'))
    try:
        user_key, user_dic = cache_get_by_id('user', 'user', user_id)
    except:
        return JsonResponse({'result': 0, 'message': '此用户不存在'})
    if user_dic['is_professional'] != 1:
        return JsonResponse({'result': 0, 'message': '此用户没有门户或正在申请，无法解除'})
    else:

        user_dic['unread_message_count'] = user_dic['unread_message_count'] + 1
        this_message = Message.objects.create(send_id=0, receiver_id=user_id, message_type=-1,
                                              author_id=user_dic['open_alex_id'], real_name=user_dic['real_name'])
        cache_set_after_create('message', 'message', this_message.id, this_message.to_dic())
        cache.delete('author:' + 'author:' + user_dic["open_alex_id"])
        celery_delete_author.delay(user_dic["open_alex_id"])
        user_dic['is_professional'] = -1
        user_dic['open_alex_id'] = None
        user_dic['work_count'] = 0
        user_dic['institution'] = None
        user_dic['institution_id'] = None
        user_dic['real_name'] = None
        message_id_list_key, message_id_list_dic = cache_get_by_id('message', 'usermessageidlist', user_id)
        message_id_list_dic['message_id_list'].append(this_message.id)
        cache.set(message_id_list_key, message_id_list_dic)
        celery_add_user_message_id_list.delay(user_id, this_message.id)
        cache.set(user_key, user_dic)
        celery_delete_user_author.delay(user_id)
        return JsonResponse({'result': 1, 'message': '解除门户成功'})
