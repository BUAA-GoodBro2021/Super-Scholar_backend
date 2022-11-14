from django.db import models


class Work(models.Model):
    open_alex_id = models.CharField('对应作品的open_alex_id', max_length=200, db_index=True, default='')
    author_id = models.CharField('上传pdf的作者的open_alex_id', max_length=200, db_index=True, default='')
    url = models.CharField('论文的访问路由', max_length=200)
    has_pdf = models.IntegerField('是否有pdf', default=-1)  # -1表示没有pdf，0表示正在审核，1表示有pdf
    is_delete = models.BooleanField('论文是否删除', default=False)

    class Meta:
        db_table = 'scholar_work'


class UploadWorkPdfFormList(models.Model):
    id_list = models.TextField('申请上传论文pdf的表单id的列表', default='[]')


class UploadWorkPdfForm(models.Model):
    user_id = models.IntegerField('发送申请的用户id')
    author_id = models.CharField('发送申请的用户认领的作者的open_alex_id', max_length=200, db_index=True, default='')
    word_id = models.CharField('申请的论文的open_alex_id', max_length=200, db_index=True, default='')
    send_time = models.TimeField('申请时间')
    url = models.CharField('论文的访问路由', max_length=200)
    flag = models.IntegerField('处理状态', default=0)  # 0表示未处理，-1表示拒绝，1表示同意
