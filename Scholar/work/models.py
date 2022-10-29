from django.db import models


class Work(models.Model):

    open_alex_id = models.CharField('对应的open_alex_id', max_length=200, db_index=True, default='')
    author_id = models.CharField('对应作者的open_alex_id', max_length=200, db_index=True, default='')
    url = models.CharField('论文的访问路由', max_length=50)
    is_delete = models.BooleanField('论文是否删除', default=False)

    class Meta:
        db_table = 'scholar_work'
