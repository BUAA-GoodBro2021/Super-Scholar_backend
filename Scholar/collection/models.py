from django.db import models


class Collection(models.Model):
    work_id = models.CharField('对应作品的open_alex_id', max_length=200)
    collection_package_id = models.IntegerField('对应收藏夹的id')

    class Meta:
        db_table = 'scholar_collection'


class CollectionPackage(models.Model):
    name = models.CharField('收藏夹的名字', max_length=50, default='默认收藏夹')
    user_id = models.IntegerField('对应用户的id', default=0)
    sum = models.IntegerField('收藏夹的收藏数目', default=0)

    is_active = models.BooleanField('是否删除', default=True)

    def to_dic(self):
        work_list = Collection.objects.filter(collection_package_id=self.id)
        work_id_list = [work.id for work in work_list]
        return {
            'id': self.id,
            'name': self.name,
            'works': work_id_list,
            'owner': self.user_id,
            'sum': self.sum,
            'is_active': self.is_active,
        }

    class Meta:
        db_table = 'scholar_collection_package'
