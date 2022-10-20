from django.db import models

# Create your models here.

class Form(models.Model):

    user_id = models.IntegerField('用户id')
    content = models.TextField('申请的内容', max_length=1024)
    is_pass = models.BooleanField('是否通过', default=False)

    class Meta:
        db_table = 'scholar_form'