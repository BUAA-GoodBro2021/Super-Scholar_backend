# 邮件信息
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.qq.com'  # 腾讯QQ邮箱SMTP服务器地址
EMAIL_PORT = 25  # SMTP服务器端口号
EMAIL_HOST_USER = '3044039051@qq.com'  # 发送邮件的QQ邮箱
EMAIL_HOST_PASSWORD = 'zosulotgxochdehe'  # 授权码
EMAIL_USE_TLS = False  # 与SMTP服务器通信时，是否启动TLS链接（安全链接）默认False
EMAIL_FROM_NAME = 'Super2021'

# 对象存储信息
bucket_secret_id = 'AKIDNZVAYfV5NO9dqmTv5zcz4sPggPr2yc07'
bucket_secret_key = 'sTnqc7LJ0Q2NREl10h8IBn8CyTigNo31'
bucket_app_id = '-1309504341'
bucket_region = 'ap-beijing'
bucket_access = 'public-read'

# MySQL数据库配置
mysql_ENGINE = 'django.db.backends.mysql'
mysql_NAME = 'scholar'
mysql_USER = 'root'
mysql_PASSWORD = 'Super2021'
mysql_HOST = '152.136.213.16'
mysql_PORT = '3306'

# Redis数据库配置
redis_BACKEND = "django_redis.cache.RedisCache"
redis_HOST = "152.136.213.16"
redis_TIMEOUT = 3600 * 24 * 2  # 缓存保存时间，单位秒，默认300
redis_MAX_ENTRIES = 6400  # 缓存最大数据条数
redis_CULL_FREQUENCY = 5  # 缓存条数到达最大值时，删除1/x的缓存数据
redis_CLIENT_CLASS = "django_redis.client.DefaultClient"
redis_CONNECTION_POOL_CLASS = "rediscluster.connection.ClusterConnectionPool"
redis_PASSWORD = "Super2021"
redis_PORT = 6379

# 查看IP地址
aliyun_appcode = '1437a6fc99dc4078bfe01338d7132c2c'  # 开通服务后 买家中心-查看AppCode

# token加密所需的密钥
TOKEN_SECRET_KEY = "django-insecure-$+i^7be6bxag@%#rv)8g=q(rp&mvdep(4lb-t5helou)=l#-2("

# 默认图片地址
default_favorite_url = 'https://global-1309504341.cos.ap-beijing.myqcloud.com/default-favorite.jpg'
default_avatar_url = 'https://global-1309504341.cos.ap-beijing.myqcloud.com/default.jpg'
default_avatar_url_match = 'https://random-avatar-1309504341.cos.ap-beijing.myqcloud.com/'
default_cover_1_url_match = 'https://random-cover-1-1309504341.cos.ap-beijing.myqcloud.com/'
default_cover_2_url_match = 'https://random-cover-2-1309504341.cos.ap-beijing.myqcloud.com/'

# 环境路由
local_base_url = "http://127.0.0.1:8000"
production_base_url = "https://scholar.super2021.com"

# OpenAlex认证邮箱
open_alex_mailto_email = "zhouenshen@buaa.edu.cn"
open_alex_base_url = "https://api.openalex.org/"
