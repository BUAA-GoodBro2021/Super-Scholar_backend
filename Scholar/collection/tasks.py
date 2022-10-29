from collection.models import CollectionPackage, Collection
from user.models import User
from Scholar.celery import app

@app.task
def celery_change_package_name(package_id, package_name):
    package = CollectionPackage.objects.get(id=package_id)
    package.name = package_name
    package.save()
    return package.to_dic()

@app.task
def celery_add_collect(package_id, work_id):

    package = Collection.objects.create(collection_package_id=package_id, work_id=work_id)
    return package.to_dic()

@app.task
def celery_cancel_collect(package_id, work_id):

    Collection.get(collection_package_id=package_id, work_id=work_id).delete()
