from celery import Celery
from django.conf import settings
from properties import *
import os

# 启动 celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Scholar.settings')

# 创建 celery
app = Celery('Scholar',
             broker='redis://:' + redis_PASSWORD + '@' + redis_HOST + ":" + str(redis_PORT) + '/1',
             backend='redis://:' + redis_PASSWORD + '@' + redis_HOST + ":" + str(redis_PORT) + '/1')

# 配置每个应用的 worker 工作
app.autodiscover_tasks(settings.INSTALLED_APPS)
