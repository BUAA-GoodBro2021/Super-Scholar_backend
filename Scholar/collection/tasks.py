from collection.models import CollectionPackage, Collection
from user.models import User, CollectionOfUser
from Scholar.celery import app
from form.models import *
from utils.Redis_utils import cache_get_by_id


@app.task
def celery_add_form_list(form_type, form_id):
    form_list = Form_list.objects.get(type=form_type)
    form_id_list = eval(form_list.Form_id_list)
    form_id_list.append(form_id)
    form_list.Form_id_list = form_id_list
    form_list.save()


@app.task
def add_collection_package_delay(package_id, user_id):
    cp = CollectionOfUser.objects.get(id=user_id)

    collection_id_list = eval(cp.collection_id_list)
    print(collection_id_list)

    collection_id_list.append(package_id)

    cp.collection_id_list = str(collection_id_list)
    cp.save()


@app.task
def celery_change_package_name(package_id, package_name):
    package = CollectionPackage.objects.get(id=package_id)
    package.name = package_name
    package.save()
    return package.to_dic()


@app.task
def celery_add_collect(package_id, work_id):
    Collection.objects.create(collection_package_id=package_id, work_id=work_id)
    cp = CollectionPackage.objects.get(id=package_id)
    cp.sum += 1
    cp.save()


@app.task
def celery_cancel_collect(package_id, work_id):
    Collection.objects.filter(collection_package_id=package_id, work_id=work_id).delete()
    cp = CollectionPackage.objects.get(id=package_id)
    cp.sum -= 1
    cp.save()


@app.task
def celery_delete_collection_package(package_id_list, user_id):
    for package_id in package_id_list:
        print(package_id)
        # 删除其中收藏的论文
        Collection.objects.filter(collection_package_id=package_id).delete()

        # 删除收藏夹
        CollectionPackage.objects.filter(id=package_id).delete()

        # 删除用户文件夹中的记录
        cp = CollectionOfUser.objects.get(id=user_id)

        collection_id_list = eval(cp.collection_id_list)
        print(collection_id_list)
        collection_id_list.remove(package_id)

        cp.collection_id_list = str(collection_id_list)
        cp.save()

