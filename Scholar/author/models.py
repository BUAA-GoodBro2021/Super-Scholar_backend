from django.db import models


class Author(models.Model):
    id = models.CharField('对应的open_alex_id', primary_key=True, max_length=200, db_index=True, default='')

    def to_dic(self):
        return {

            'open_alex_id': self.id,

        }

    class Meta:
        db_table = 'scholar_author'
