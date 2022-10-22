from django.db import models


class User(models.Model):
    # 基础信息
    username = models.CharField('用户名', max_length=100, default='')
    password = models.CharField('密码', max_length=32)
    email = models.EmailField()
    introduction = models.TextField('自我介绍', blank=True, max_length=2048,
                                    default='Leave something to help others get to know you better!')
    is_active = models.BooleanField('邮箱是否验证', default=False)

    # 头像
    avatar_url = models.CharField('用户头像路径', max_length=128, default='')
    avatar = models.FileField('用户头像', upload_to='', default='')

    # 权限判断
    is_professional = models.BooleanField('是否认证', default=False)

    # 实体属性
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    updated_time = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'scholar_user'
