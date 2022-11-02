from django.db import models


class Form(models.Model):

    user_id = models.IntegerField('用户id', default=0)
    content = models.TextField('申请的内容', max_length=1024, default='')
    author_id = models.CharField('对应的open_alex_id', max_length=200, default='')
    is_pass = models.BooleanField('是否通过', default=False)

    class Meta:
        db_table = 'scholar_form'
