from django.db import models


class FormList(models.Model):
    form_id_list = models.TextField('未处理的申请的id的列表', max_length=1024, default='[]')
    id = models.IntegerField('申请处理状态', primary_key=True)  # 0表示正在审批，1表示申请通过，2表示申请拒绝

    def to_dic(self):
        return {
            'id': self.id,
            'Form_id_list': eval(self.form_id_list),
        }


class Form(models.Model):
    id = models.IntegerField('用户id', primary_key=True)
    content = models.TextField('申请的内容', max_length=1024, default='')
    author_id = models.CharField('对应的open_alex_id', max_length=200, default='')
    is_pass = models.IntegerField('是否通过', default=0)  # 0表示正在审批，1表示申请通过，2表示申请拒绝

    def to_dic(self):
        return {
            'user_id': self.id,
            'content': self.content,
            'author_id': self.author_id,
            'is_pass': self.is_pass,
        }

    class Meta:
        db_table = 'scholar_form'
