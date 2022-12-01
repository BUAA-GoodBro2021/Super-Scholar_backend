from django.db import models


class History(models.Model):
    id = models.IntegerField('用户的id', primary_key=True, default=0)  # user_id
    history_list = models.TextField('用户的搜索历史', default='')

    class Meta:
        db_table = 'scholar_history'

    def to_dic(self):
        history_list = self.history_list.split('|')
        history_list = [history_list_info for history_list_info in history_list if history_list_info != ""]
        return {
            'id': self.id,
            'history_list': history_list,
        }
