from django.db import models
from django.utils.timezone import now


class Work(models.Model):
    user_id = models.IntegerField('上传pdf的用户id', null=True)
    id = models.CharField('对应作品的open_alex_id', primary_key=True, max_length=200, db_index=True, default='')
    author_id = models.CharField('上传pdf的作者的open_alex_id', max_length=200, db_index=True, default='')
    url = models.CharField('论文的访问路由', max_length=200, null=True)
    pdf = models.FileField('文章pdf', upload_to='', default='')
    has_pdf = models.IntegerField('是否有pdf', default=-1)  # -1表示没有pdf，0表示正在审核，1表示有pdf
    send_time = models.DateTimeField('上传时间')
    last_user_id = models.IntegerField('上一个上传pdf的用户id', null=True)
    last_author_id = models.CharField('上一个上传pdf的作者的open_alex_id', max_length=200, db_index=True, default='')
    last_url = models.CharField('上次论文的访问路由', max_length=200, null=True)
    last_pdf = models.FileField('上次文章pdf', upload_to='', null=True)
    last_has_pdf = models.IntegerField('上次是否有pdf', default=-1)  # -1表示没有pdf，0表示正在审核，1表示有pdf
    last_send_time = models.DateTimeField('上次上传时间', null=True)

    # is_delete = models.BooleanField('论文是否删除', default=False)

    def to_dic(self):
        return {
            'id': self.id,

            'user_id': self.user_id,
            'author_id': self.author_id,
            'pdf': self.pdf.name,
            'url': self.url,
            'has_pdf': self.has_pdf,
            'send_time': self.send_time,

            'last_user_id': self.last_user_id,
            'last_author_id': self.last_author_id,
            'last_pdf': self.last_pdf.name,
            'last_url': self.last_url,
            'last_has_pdf': self.last_has_pdf,
            'last_send_time': self.last_send_time
        }

    class Meta:
        db_table = 'scholar_work'


class File(models.Model):
    pdf = models.FileField('pdf', upload_to='', null=True)


class UploadWorkPdfFormList(models.Model):
    id_list = models.TextField('申请上传论文pdf的表单id的列表', default='[]')

    def to_dic(self):
        return {
            'id': self.id,
            'id_list': eval(self.id_list)
        }


class UploadWorkPdfForm(models.Model):
    user_id = models.IntegerField('发送申请的用户id')
    author_id = models.CharField('发送申请的用户认领的作者的open_alex_id', max_length=200, db_index=True, default='')
    word_id = models.CharField('申请的论文的open_alex_id', max_length=200, db_index=True, default='')
    send_time = models.TimeField('申请时间')
    url = models.CharField('论文的访问路由', max_length=200)
    flag = models.IntegerField('处理状态', default=0)  # 0表示未处理，-1表示拒绝，1表示同意
