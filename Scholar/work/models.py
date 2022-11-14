from django.db import models


class Work(models.Model):
    open_alex_id = models.CharField('对应的open_alex_id', max_length=200, db_index=True, default='')
    author_id = models.CharField('对应作者的open_alex_id', max_length=200, db_index=True, default='')
    url = models.CharField('论文的访问路由', max_length=200)
    is_delete = models.BooleanField('论文是否删除', default=False)

    class Meta:
        db_table = 'scholar_work'


class UploadWorkPdfForm(models.Model):
    user_id = models.IntegerField('发送申请的用户id')
    author_id = models.CharField('发送申请的用户认领的作者的open_alex_id', max_length=200, db_index=True, default='')
    word_id = models.CharField('申请的论文的open_alex_id', max_length=200, db_index=True, default='')
    send_time = models.TimeField('申请时间')
    url = models.CharField('论文的访问路由', max_length=200)
    flag = models.IntegerField('处理状态', default=0)  # 0表示未处理，-1表示拒绝，1表示同意
