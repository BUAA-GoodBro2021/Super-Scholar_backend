from Scholar.celery import app
from form.models import *
from author.models import *
from user.models import *


@app.task
def celery_claim_author(author_id, user_id):
    user = User.objects.get(id=user_id)
    user.is_professional = 0
    user.open_alex_id = author_id
    user.save()
    print("celery_claim_author")


@app.task
def celery_add_form_list(form_type, form_id):
    form_list = Form_list.objects.get(id=form_type)
    form_id_list = eval(form_list.Form_id_list)
    form_id_list.append(form_id)
    print(form_id_list)
    form_list.Form_id_list = str(form_id_list)
    form_list.save()
    print('celery_add_form_list')


@app.task
def celery_remove_form_list(form_type, form_id):
    form_list = Form_list.objects.get(id=form_type)
    form_id_list = eval(form_list.Form_id_list)
    form_id_list.remove(form_id)
    print(form_id_list)
    form_list.Form_id_list = str(form_id_list)
    form_list.save()
    print('celery_remove_form_list')


@app.task
def celery_del_form(form_id):
    form = Form.objects.get(id=form_id)
    form.delete()
    print('celery_change_form_pass')


# @app.task
# def celery_change_author_pass(result, user_id):
#     author = Author.objects.get(id=user_id)
#     author.is_pass = result
#     author.save()
#     print('celery_change_author_pass')


@app.task
def celery_change_user_pass(deal_result, user_id):
    user = User.objects.get(id=user_id)
    if deal_result == 1:
        user.is_professional = 1
    else:
        user.is_professional = -1
        user.open_alex_id = None
    user.save()
    print('celery_change_user_pass')
