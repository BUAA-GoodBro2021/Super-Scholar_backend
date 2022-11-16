from django.db import models


class History(models.Model):
    work_id = models.CharField('对应作品的open_alex_id', max_length=200, default='')
    user_id = models.IntegerField('对应用户的id', default=0)
    created_time = models.DateTimeField('浏览时间', auto_now_add=True)

    class Meta:
        db_table = 'scholar_history'
