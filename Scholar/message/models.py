from django.db import models


class Message(models.Model):

    content = models.TextField('消息的内容', max_length=1024, default='')
    receiver_id = models.IntegerField('接受者的用户id', default=0)
    send_time = models.DateTimeField('发送时间', auto_now_add=True)

    class Meta:
        db_table = 'scholar_message'
