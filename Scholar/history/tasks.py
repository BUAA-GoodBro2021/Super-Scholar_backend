from Scholar.celery import app
from history.models import History


@app.task
def celery_update_history(user_id, history_list):
    history = History.objects.get(id=user_id)
    history_list_string = '|'.join(history_list)
    history.history_list = history_list_string
    history.save()
    return history.to_dic()
