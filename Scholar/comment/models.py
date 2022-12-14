from django.db import models


class Comment(models.Model):
    user_id = models.IntegerField('对应用户的id', db_index=True, default=0)
    level = models.IntegerField('评论级别', default=0)  # 0 -> 顶级评论, 1 -> 回复评论
    father_id = models.IntegerField('对应父评论的id', default=0)
    ancestor_id = models.IntegerField('对应顶级评论的id', default=0)
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    work_id = models.CharField('评论文章的id', max_length=200, default="")
    work_name = models.CharField('评论文章的题目', max_length=1024, default="")
    content = models.TextField('评论内容', max_length=1024, default="")
    is_deleted = models.BooleanField('评论是否被删除', default=False)
    reply_user_id = models.IntegerField('回复评论的用户id', default=0)

    class Meta:
        db_table = 'scholar_comment'

    def to_dic(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'level': self.level,
            'father_id': self.father_id,
            'ancestor_id': self.ancestor_id,
            'created_time': self.created_time,
            'work_id': self.work_id,
            'work_name': self.work_name,
            'content': self.content,
            'is_deleted': self.is_deleted,
            'reply_user_id': self.reply_user_id,
        }


class CommentOfWorks(models.Model):
    id = models.CharField('评论文章的id', primary_key=True, max_length=200, default="")  # work_id
    comment_id_list = models.TextField('评论id', max_length=20000, default='[]')  # 其中只包含0级评论的id

    class Meta:
        db_table = 'scholar_comment_of_works'

    def to_dic(self):
        comment_id_list = eval(self.comment_id_list)
        # print(comment_id_list)
        return {
            'work_id': self.id,
            'comment_id_list': comment_id_list,
        }


class CommentOfComments(models.Model):
    id = models.IntegerField('回复的评论的id', primary_key=True, default=0)  # comment_id
    comment_id_list = models.TextField('评论id', max_length=20000, default='[]')

    class Meta:
        db_table = 'scholar_comment_of_comments'

    def to_dic(self):
        comment_id_list = eval(self.comment_id_list)
        # print(comment_id_list)
        return {
            'comment_id': self.id,
            'comment_id_list': comment_id_list,
        }
