from django.db import models

# Create your models here.

class Author(models.Model):

    open_alex_id = models.CharField('对应的open_alex_id', max_length=50, db_index=True)
    user_id = models.IntegerField('对应的用户id')

    class Meta:

        db_table = 'scholar_author'