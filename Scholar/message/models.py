from django.db import models


class UserMessageIdList(models.Model):
    id = models.IntegerField('接受消息用户的id', primary_key=True)
    message_id_list = models.TextField('用户接受的消息的id列表', default='[]')

    def to_dic(self):
        return {
            'id': self.id,
            'message_id_list': eval(self.message_id_list)
        }


class Message(models.Model):
    send_id = models.IntegerField('发送消息用户的id', default=0)  # 0表示管理员或者系统消息，其他表示用户的id
    receiver_id = models.IntegerField('接受者的用户id', default=0)
    send_time = models.DateTimeField('发送时间', auto_now_add=True)

    message_type = models.IntegerField(
        '消息的类型',
        default=-1)  # -1表示管理员解除用户的门户，0表示管理员拒绝用户的申请门户，1表示管理员同意用户的申请门户，2表示管理员拒绝了用户的上传pdf申请，3表示管理员同意了用户的上传pdf申请,4表示评论消息

    author_id = models.CharField('用户申请的作者的open_alex的id', max_length=1024, default='')
    real_name = models.CharField('用户申请的作者的open_alex的name', max_length=1024, default='')
    institution = models.CharField('用户申请的作者所属机构名称', max_length=200, default='')

    work_name = models.CharField('文章名称', max_length=1024, default='')
    work_open_alex_id = models.CharField('文章的open_alex的id', max_length=1024, default='')

    content = models.TextField('被评论的内容', max_length=1024, default='')
    reply = models.TextField('回复的内容', max_length=1024, default='')

    pdf = models.CharField('文章pdf', max_length=200, default='')
    url = models.CharField('论文的访问路由', max_length=200, null=True)

    def to_dic(self):
        return {
            'send_id': self.send_id,
            'message_type': self.message_type,
            # 0表示管理S员拒绝用户的申请门户，1表示管理员同意用户的申请门户，2表示管理员拒绝了用户的上传pdf申请，3表示管理员同意了用户的上传pdf申请,4表示评论消息
            'content': self.content,
            'work_name': self.work_name,
            'reply': self.reply,
            'work_open_alex_id': self.work_open_alex_id,
            'author_id': self.author_id,
            'real_name': self.real_name,
            'institution': self.institution,
            'receiver_id': self.receiver_id,
            'send_time': self.send_time,
            'pdf': self.pdf,
            'url': self.url
        }

    class Meta:
        db_table = 'scholar_message'
