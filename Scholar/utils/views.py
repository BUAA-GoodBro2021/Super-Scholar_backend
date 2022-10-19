from django.core.cache import cache
from django.http import HttpResponse


def clear_redis_all(request):
    cache.clear()
    return HttpResponse("OK")
