from django.db import models


class Author(models.Model):
    open_alex_id = models.CharField('对应的open_alex_id', max_length=200, db_index=True, default='')
    id = models.IntegerField('对应的用户id', default=0, primary_key=True)
    is_pass = models.IntegerField('是否通过', default=0)  # 0表示正在审批，1表示申请通过，-1表示申请拒绝

    def to_dic(self):
        return {
            'user_id': self.id,
            'open_alex_id': self.open_alex_id,
            'is_pass': self.is_pass,
        }

    class Meta:
        db_table = 'scholar_author'
