from random import Random
from django.http import JsonResponse
from django.utils.timezone import now

from Scholar.settings import BASE_DIR
from utils.Bucket_utils import Bucket
from utils.Login_utils import login_checker
from utils.Redis_utils import *
from work.tasks import *


# 生成随机字符串
def create_code(random_length=6):
    str_code = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars) - 1
    random = Random()
    for i in range(random_length):
        str_code += chars[random.randint(0, length)]
    return str_code


@login_checker
def user_upload_pdf(request):  # 用户上传pdf
    user_id = request.user_id
    # 获取用户上传的头像并保存
    pdf = request.FILES.get("pdf", None)
    if not pdf:
        result = {'result': 0, 'message': r"请上传图片！"}
        return JsonResponse(result)
    # 获取文件尾缀并
    # 修改名称
    suffix = '.' + (pdf.name.split("."))[-1]
    work_id = request.POST.get('work_id', '')
    work_name = request.POST.get('work_name', "")
    author_id = request.POST.get('author_id', '')
    # 先生成一个随机 Key 保存在桶中进行审核
    key = create_code()
    pdf.name = str(work_id) + key + suffix
    try:
        this_work = Work.objects.create(id=work_id, author_id=author_id, work_name=work_name, pdf=pdf, has_pdf=0,
                                        user_id=user_id,
                                        send_time=now())
    except:
        return JsonResponse({'result': 0, 'message': r"当前论文已有pdf或正在审核，请刷新页面！"})
    # 常见对象存储的对象
    bucket = Bucket()

    upload_result = bucket.upload_file("pdf", work_id + key + suffix, pdf.name)
    # 上传审核
    if upload_result == -1:
        result = {'result': 0, 'message': r"上传失败！"}
        os.remove(os.path.join(BASE_DIR, "media/" + pdf.name))
        print(1)
        return JsonResponse(result)
    # 上传是否可以获取路径
    url = bucket.query_object("pdf", work_id + key + suffix)
    if not url:
        os.remove(os.path.join(BASE_DIR, "media/" + pdf.name))
        result = {'result': 0, 'message': r"上传失败！"}
        return JsonResponse(result)
    this_work.url = url
    cache_set_after_create('work', 'work', this_work.id, this_work.to_dic())

    celery_save_pdf_url.delay(this_work.id, url)
    # 删除本地文件
    os.remove(os.path.join(BASE_DIR, "media/" + pdf.name))
    upload_pdf_form_list_key, upload_pdf_form_list_dic = cache_get_by_id('work', 'uploadworkpdfformlist', 1)
    upload_pdf_form_list_dic['id_list'].append(this_work.id)
    cache.set(upload_pdf_form_list_key, upload_pdf_form_list_dic)
    celery_add_pdf_upload_form_list.delay(1, this_work.id)
    return JsonResponse({'result': 1, 'message': r"上传成功，请等待管理员审核！"})


@login_checker
def user_re_upload_pdf(request):  # 用户再次上传pdf
    user_id = request.user_id
    # 获取用户上传的头像并保存
    pdf = request.FILES.get("pdf", None)
    if not pdf:
        result = {'result': 0, 'message': r"请上传图片！"}
        return JsonResponse(result)
    # 获取文件尾缀并
    # 修改名称
    suffix = '.' + (pdf.name.split("."))[-1]

    work_id = request.POST.get('work_id', '')
    # user_id = request.POST.get('user_id', "")
    author_id = request.POST.get('author_id', '')
    try:
        work_key, work_dic = cache_get_by_id('work', 'work', work_id)
    except:
        return JsonResponse({'result': 0, 'message': r"此论文暂无pdf"})
    if work_dic['has_pdf'] == 0:
        return JsonResponse({'result': 0, 'message': r"原pdf正在审核，待审核完毕后上传！"})
    # 先生成一个随机 Key 保存在桶中进行审核
    key = create_code()
    pdf.name = str(work_id) + key + suffix
    File.objects.create(pdf=pdf)
    # 常见对象存储的对象
    bucket = Bucket()

    upload_result = bucket.upload_file("pdf", work_id + key + suffix, pdf.name)
    # 上传审核
    if upload_result == -1:
        result = {'result': 0, 'message': r"上传失败！"}
        os.remove(os.path.join(BASE_DIR, "media/" + pdf.name))
        return JsonResponse(result)
    # 上传是否可以获取路径
    url = bucket.query_object("pdf", work_id + key + suffix)
    if not url:
        os.remove(os.path.join(BASE_DIR, "media/" + pdf.name))
        result = {'result': 0, 'message': r"上传失败！"}
        return JsonResponse(result)

    work_dic['last_user_id'] = work_dic['user_id']
    work_dic['last_author_id'] = work_dic['author_id']
    work_dic['last_pdf'] = work_dic['pdf']
    work_dic['last_url'] = work_dic['url']
    work_dic['last_has_pdf'] = work_dic['has_pdf']
    work_dic['last_send_time'] = work_dic['send_time']

    work_dic['user_id'] = user_id
    work_dic['author_id'] = author_id
    work_dic['pdf'] = pdf.name
    work_dic['url'] = url
    work_dic['has_pdf'] = 0
    work_dic['send_time'] = now()

    cache.set(work_key, work_dic)
    celery_re_upload_pdf(work_id, user_id, url, author_id, pdf.name)
    # 删除本地文件
    os.remove(os.path.join(BASE_DIR, "media/" + pdf.name))
    upload_pdf_form_list_key, upload_pdf_form_list_dic = cache_get_by_id('work', 'uploadworkpdfformlist', 1)
    upload_pdf_form_list_dic['id_list'].append(work_id)
    cache.set(upload_pdf_form_list_key, upload_pdf_form_list_dic)
    celery_add_pdf_upload_form_list.delay(1, work_id)
    return JsonResponse({'result': 1, 'message': r"上传成功，请等待管理员审核！"})


@login_checker
def manager_check_upload_pdf(request):  # 管理员查看pdf上传申请列表
    user_id = request.user_id
    super_user_key, super_user_dic = cache_get_by_id('user', 'user', user_id)
    if not super_user_dic['is_super']:
        return JsonResponse({'result': 0, 'message': '当前用户不是管理员'})
    upload_pdf_form_list_key, upload_pdf_form_list_dic = cache_get_by_id('work', 'uploadworkpdfformlist', 1)
    upload_pdf_form_id_list = upload_pdf_form_list_dic['id_list']
    upload_pdf_form_dic_list = []
    for upload_pdf_form_id in upload_pdf_form_id_list:
        try:
            work_id, work_dic = cache_get_by_id('work', 'work', upload_pdf_form_id)
        except:
            return JsonResponse({'result': 0, 'message': '此论文没有上传pdf申请'})
        upload_pdf_form_dic_list.append(work_dic)

    return JsonResponse({'result': 1, 'message': '获取申请成功', 'upload_pdf_form_dic_list': upload_pdf_form_dic_list})


@login_checker
def manager_deal_upload_pdf(request):  # 管理员处理pdf上传申请
    user_id = request.user_id

    super_user_key, super_user_dic = cache_get_by_id('user', 'user', user_id)
    if not super_user_dic['is_super']:
        return JsonResponse({'result': 0, 'message': '当前用户不是管理员'})

    data_json = json.loads(request.body.decode())
    print(data_json)
    work_id = data_json.get('work_id')
    deal_result = data_json.get('deal_result')
    try:
        work_key, work_dic = cache_get_by_id('work', 'work', work_id)
    except:
        return JsonResponse({'result': 0, 'message': '此论文不存在'})

    upload_pdf_form_list_key, upload_pdf_form_list_dic = cache_get_by_id('work', 'uploadworkpdfformlist', 1)
    upload_pdf_form_id_list = upload_pdf_form_list_dic['id_list']
    upload_pdf_form_id_list.remove(work_id)
    upload_pdf_form_list_dic['id_list'] = upload_pdf_form_id_list
    cache.set(upload_pdf_form_list_key, upload_pdf_form_list_dic)

    celery_remove_pdf_upload_form_list(1, work_id)

    if deal_result == 1:
        work_dic['has_pdf'] = 1
        cache.set(work_key, work_dic)
        celery_change_pdf_upload_form_has(work_id)

    elif deal_result == -1:
        if work_dic['last_has_pdf'] == -1:
            cache.delete(work_key)
            celery_delete_pdf_upload_form.delay(work_id)
        elif work_dic['last_has_pdf'] == 1:
            work_dic['user_id'] = work_dic['last_user_id']
            work_dic['author_id'] = work_dic['last_author_id']
            work_dic['pdf'] = work_dic['last_pdf']
            work_dic['url'] = work_dic['last_url']
            work_dic['has_pdf'] = work_dic['last_has_pdf']
            work_dic['send_time'] = work_dic['last_send_time']
            cache.set(work_key, work_dic)
            celery_recover_work_pdf.delay(work_id)
    return JsonResponse({"result": 1, "message": '处理成功'})


@login_checker
def user_give_up_upload_pdf(request):
    user_id = request.user_id
    data_json = json.loads(request.body.decode())
    print(data_json)
    work_id = data_json.get('work_id')
    author_id = data_json.get('author_id')
    try:
        user_key, user_dic = cache_get_by_id('user', 'user', user_id)
    except:
        return JsonResponse({"result": 0, "message": '用户不存在'})

    try:
        work_key, work_dic = cache_get_by_id('work', 'work', work_id)
    except:
        return JsonResponse({"result": 0, "message": '作品暂未上传pdf'})
    if work_dic['user_id'] != user_id:
        return JsonResponse({"result": 0, "message": '您不是上传此pdf的用户，删除此pdf请联系管理员'})
    has_pdf = work_dic['has_pdf']
    if has_pdf == 1:
        cache.delete(work_key)
        celery_delete_work_pdf.delay(work_id)
    elif work_dic['has_pdf'] == 0:
        upload_pdf_form_list_key, upload_pdf_form_list_dic = cache_get_by_id('work', 'uploadworkpdfformlist', 1)
        upload_pdf_form_id_list = upload_pdf_form_list_dic['id_list']
        upload_pdf_form_id_list.remove(work_id)
        upload_pdf_form_list_dic['id_list'] = upload_pdf_form_id_list
        cache.set(upload_pdf_form_list_key, upload_pdf_form_list_dic)
        if work_dic['last_has_pdf'] == 1:
            work_dic['user_id'] = work_dic['last_user_id']
            work_dic['author_id'] = work_dic['last_author_id']
            work_dic['pdf'] = work_dic['last_pdf']
            work_dic['url'] = work_dic['last_url']
            work_dic['has_pdf'] = work_dic['last_has_pdf']
            work_dic['send_time'] = work_dic['last_send_time']
            cache.set(work_key, work_dic)
            celery_recover_work_pdf.delay(work_id)
        else:
            cache.delete(work_key)
            celery_delete_work_pdf.delay(work_id)
    if has_pdf == 1:
        return JsonResponse({"result": 1, "message": '删除pdf成功'})
    else:
        return JsonResponse({"result": 1, "message": '取消上传pdf成功'})
