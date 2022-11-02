from Scholar.celery import app
from follow.models import Follow


@app.task
def celery_add_follow(user_id, author_id):
    Follow.objects.create(user_id=user_id, author_id=author_id)


@app.task
def celery_delete_follow(user_id, author_id):
    Follow.objects.get(user_id=user_id, author_id=author_id).delete()
