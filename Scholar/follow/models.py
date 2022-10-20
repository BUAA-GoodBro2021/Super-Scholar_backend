from django.db import models

# Create your models here.
class Follow( models.Model ):

    follow_id = models.IntegerField('关注人的id')
    followed_id = models.IntegerField('被关注人的id')

    class Meta:

        db_table = 'scholar_follow'