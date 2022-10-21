from django.db import models


class Message(models.Model):
    content = models.TextField('消息的内容', max_length=1024)
    receiver_id = models.IntegerField('接受者的用户id')
    send_time = models.DateTimeField('发送时间', auto_now_add=True)

    class Meta:
        db_table = 'scholar_message'
