from collection.models import CollectionPackage
from user.models import User
from Scholar.celery import app

@app.task
def celery_change_package_name(package_id, package_name):
    package = CollectionPackage.objects.get(id=package_id)
    package.name = package_name
    package.save()
    return package.to_dic()