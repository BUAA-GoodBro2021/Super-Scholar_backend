import json
from django.core.cache import cache
from user.models import *
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.db.models import *
from collection.models import *
from collection.tasks import *
from utils.Login_utils import hash_encode
from utils.Redis_utils import cache_get_by_id

from utils.Sending_utils import *

@login_checker
def add_collection_package( request ):
    if request.method == 'POST':
        # 获取表单信息
        data_json = json.loads(request.body.decode())
        user_id = request.user_id
        package_name = data_json.get('package_name', '默认收藏夹')

        # 异常处理
        # 收藏夹命名为空
        if len(package_name) == 0:
            result = {'result': 0, 'message': r'收藏夹名不允许为空!'}
            return JsonResponse(result)

        i = 1
        # 获取当前用户建立的所有收藏夹
        user_package = CollectionPackage.objects.filter(user_id=user_id)
        print(user_package)
        # 寻找重复名称进行修改
        test_name = package_name
        while user_package.filter(name=test_name).exists():
            test_name = package_name + f"({i})"
            print(i)
            i = i + 1

        package_name = test_name

        # 创建收藏夹
        cp = CollectionPackage.objects.create(name=package_name, user_id=user_id)
        # 存储至缓存
        cp_key, cp_dict = cache_get_by_id('collection', 'collectionpackage', cp.id )

        result = {'result': 1, 'message': r"添加成功！", 'collection_package': cp_dict}
        return JsonResponse(result)

    else:
        result = {'result': 0, 'message': r"请求方式错误！"}
        return JsonResponse(result)

@login_checker
def change_package_name( request ):
    if request.method == 'POST':
        # 获取表单信息
        data_json = json.loads(request.body.decode())
        user_id = request.user_id
        package_name = data_json.get('package_name', '默认收藏夹')
        package_id =data_json.get('package_id', '-1')

        # 获取当前用户建立的所有收藏夹
        user_package = CollectionPackage.objects.filter(user_id=user_id)
        # 异常处理
        # 收藏夹命名为空
        if len(package_name) == 0:
            result = {'result': 0, 'message': r'收藏夹名不允许为空!'}
            return JsonResponse(result)

        package = user_package.filter(id=package_id).first()
        # 收藏夹不存在
        if not package:
            result = {'result': 0, 'message': r'收藏夹名不存在!'}
            return JsonResponse(result)

        # 两次命名相同
        if package.name != package_name:
            i = 1
            # 寻找重复名称进行修改
            test_name = package_name
            while user_package.filter(name=test_name).exists():
                test_name = package_name + f"({i})"
                print(i)
                i = i + 1
                package_name = test_name

            # 存储至缓存
            cp_key, cp_dict = cache_get_by_id('collection', 'collectionpackage', package_id )
            # 修改缓存信息
            cp_dict['name'] = package_name
            # 同步数据库
            celery_change_package_name.delay(package_id, package_name)
        else:
            cp_dict = package.to_dic()

        result = {'result': 1, 'message': r"修改成功！", 'collection_package': cp_dict}
        return JsonResponse(result)

    else:
        result = {'result': 0, 'message': r"请求方式错误！"}
        return JsonResponse(result)