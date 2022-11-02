from django.db import models


class Follow(models.Model):
    user_id = models.IntegerField('关注人的id', default=0)
    author_id = models.CharField('被关注人的id', max_length=200, default='')

    class Meta:
        db_table = 'scholar_follow'
