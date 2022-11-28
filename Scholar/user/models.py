from django.db import models

from collection.models import CollectionPackage
from follow.models import Follow


class UserList(models.Model):
    id_list = models.TextField('用户的id的列表', max_length=1024, default='[]')

    def to_dic(self):
        return {
            'id': self.id,
            'id_list': eval(self.id_list)
        }


class User(models.Model):
    # 基础信息
    username = models.CharField('用户名', max_length=100, default='')
    password = models.CharField('密码', max_length=32)
    email = models.EmailField()
    introduction = models.TextField('自我介绍', blank=True, max_length=2048,
                                    default='Leave something to help others get to know you better!')
    is_active = models.BooleanField('邮箱是否已经验证', default=False)
    is_super = models.BooleanField('是否为超管', default=False)

    # 头像
    avatar_url = models.CharField('用户头像路径', max_length=128, default='')
    avatar = models.FileField('用户头像', upload_to='', default='')

    # 权限判断
    is_professional = models.IntegerField('是否认证', default=-1)  # -1未认证，0正在申请，1已认证
    open_alex_id = models.CharField('对应的open_alex_id', max_length=200, db_index=True, default='', null=True)
    real_name = models.CharField('对应的作者真名', max_length=200, db_index=True, default='', null=True)
    institution = models.CharField('作者的机构', max_length=200, db_index=True, default='', null=True)
    institution_id = models.CharField('作者的机构的open_alex_id', max_length=200, db_index=True, default='', null=True)
    work_count = models.IntegerField('作者作品数量', default=0)
    # 实体属性
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    updated_time = models.DateTimeField('更新时间', auto_now=True)

    # 未读消息个数
    unread_message_count = models.IntegerField('未读消息个数', default=0)

    class Meta:
        db_table = 'scholar_user'

    def to_dic(self):
        return {
            'user_id': self.id,
            'username': self.username,
            'email': self.email,

            "avatar_url": self.avatar_url,

            'is_active': self.is_active,
            'is_super': self.is_super,
            'is_professional': self.is_professional,
            'real_name': self.real_name,
            'institution': self.institution,
            'institution_id': self.institution_id,
            'work_count': self.work_count,
            'open_alex_id': self.open_alex_id,
            'created_time': self.created_time,
            'updated_time': self.updated_time,
            'unread_message_count': self.unread_message_count,
        }


class FollowOfUser(models.Model):
    id = models.IntegerField('用户的id', primary_key=True, default=0)  # user_id
    follow_id_list = models.TextField('被关注人的id列表', max_length=20000, default='')

    class Meta:
        db_table = 'scholar_follow_of_user'

    def to_dic(self):
        follow_id_list = self.follow_id_list.split('#')
        follow_id_list = [follow_id for follow_id in follow_id_list if follow_id != '']
        print(follow_id_list)
        return {
            'user_id': self.id,
            'follow_id_list': follow_id_list,
        }


class CollectionOfUser(models.Model):
    id = models.IntegerField('用户的id', primary_key=True, default=0)  # user_id
    collection_id_list = models.TextField('用户收藏夹的id列表', max_length=20000, default='')

    class Meta:
        db_table = 'scholar_collection_of_user'

    def to_dic(self):
        collection_id_list = self.collection_id_list.split(' ')
        collection_id_list = [int(collection_id) for collection_id in collection_id_list if collection_id != '']
        print(collection_id_list)
        return {
            'user_id': self.id,
            'collection_id_list': collection_id_list,
        }
