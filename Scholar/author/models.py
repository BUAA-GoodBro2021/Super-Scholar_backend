from django.db import models


class Author(models.Model):

    open_alex_id = models.CharField('对应的open_alex_id', max_length=200, db_index=True, default='')
    user_id = models.IntegerField('对应的用户id', default=0)

    class Meta:
        db_table = 'scholar_author'
