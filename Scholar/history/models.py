from django.db import models


class History(models.Model):
    id = models.IntegerField('用户的id', primary_key=True, default=0)  # user_id
    history_list = models.TextField('用户的搜索历史', default='')

    class Meta:
        db_table = 'scholar_history'

    def to_dic(self):
        history_list = self.history_list.split('|')
        return {
            'id': self.id,
            'history_list': history_list,
        }
