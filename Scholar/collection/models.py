from django.db import models

# Create your models here.
class Collection(models.Model):

    user_id = models.IntegerField('用户的id')
    work_id = models.CharField('对应作品的open_alex_id', max_length=50)
    collection_package_id = models.IntegerField('对应收藏夹的id')

    class Meta:

        db_table = 'scholar_collection'


class CollectionPackage(models.Model):

    name = models.CharField('收藏夹的名字', max_length=50, default='默认收藏夹')
    user_id = models.IntegerField('对应用户的id', default=0)
    sum = models.IntegerField('收藏夹的收藏数目', default=0)

    class Meta:

        db_table = 'scholar_collection_package'