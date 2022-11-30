from django.db import models


class History(models.Model):
    user_id = models.IntegerField('用户的id', default=0)
    history_list = models.TextField('用户的搜索历史', default='')

    class Meta:
        db_table = 'scholar_history'

    def to_dic(self):
        history_list = self.history_list.split('|')
        return {
            'id': self.id,
            'user_id': self.user_id,
            'history_list': history_list,
        }
