from Scholar.celery import app
from form.models import *


@app.task
def celery_add_form_list(form_type, form_id):
    form_list = Form_list.objects.get(id=form_type)
    form_id_list = eval(form_list.Form_id_list)
    form_id_list.append(form_id)
    form_list.Form_id_list = form_id_list
    form_list.save()


