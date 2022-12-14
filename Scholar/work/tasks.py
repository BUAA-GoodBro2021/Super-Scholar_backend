from django.utils.timezone import now

from Scholar.celery import app
from message.models import UserMessageIdList
from work.models import *
from user.models import *


@app.task
def celery_save_pdf_url(model_id, url):
    print(url)
    work_model = Work.objects.get(id=model_id)
    work_model.url = url
    work_model.save()
    print("save_pdf_url")


@app.task
def celery_add_pdf_upload_form_list(model_id, work_id):
    this_list = UploadWorkPdfFormList.objects.get(id=model_id)
    id_list = eval(this_list.id_list)
    id_list.append(work_id)
    this_list.id_list = id_list
    this_list.save()
    print("celery_add_pdf_upload_form_list")


@app.task
def celery_remove_pdf_upload_form_list(model_id, work_id):
    this_list = UploadWorkPdfFormList.objects.get(id=model_id)
    id_list = eval(this_list.id_list)
    id_list.remove(work_id)
    this_list.id_list = id_list
    this_list.save()
    print("celery_add_pdf_upload_form_list")


@app.task
def celery_change_pdf_upload_form_has(model_id):
    this_work = Work.objects.get(id=model_id)
    this_work.has_pdf = 1
    this_work.save()
    print("celery_change_pdf_upload_form_has")


@app.task
def celery_delete_pdf_upload_form(model_id):
    this_work = Work.objects.get(id=model_id)
    this_work.delete()
    print("celery_delete_pdf_upload_form")


@app.task
def celery_recover_work_pdf(model_id):
    this_work = Work.objects.get(id=model_id)
    this_work.has_pdf = this_work.last_has_pdf
    this_work.pdf = this_work.last_pdf
    this_work.url = this_work.last_url
    this_work.user_id = this_work.last_user_id
    this_work.author_id = this_work.last_author_id
    this_work.save()
    print("celery_recover_work_pdf")


@app.task
def celery_re_upload_pdf(model_id, user_id, url, author_id, pdf_name):
    this_work = Work.objects.get(id=model_id)
    this_work.last_author_id = this_work.author_id
    this_work.author_id = author_id
    this_work.last_user_id = this_work.user_id
    this_work.user_id = user_id
    this_work.last_url = this_work.url
    this_work.url = url
    this_work.last_pdf = this_work.pdf
    this_work.pdf = pdf_name
    this_work.has_pdf = 0
    this_work.last_has_pdf = 1
    this_work.last_send_time = this_work.send_time
    this_work.send_time = now()
    this_work.save()
    print("celery_re_upload_pdf")


@app.task
def celery_delete_work_pdf(model_id):
    this_work = Work.objects.get(id=model_id)
    this_work.delete()
    print("celery_delete_work_pdf")


@app.task
def celery_add_user_message_id_list(user_id, message_id):
    user_message_list = UserMessageIdList.objects.get(id=user_id)
    message_id_list = eval(user_message_list.message_id_list)
    message_id_list.append(message_id)
    user_message_list.message_id_list = str(message_id_list)
    user_message_list.save()
    print('celery_add_user_message_id_list')


@app.task
def celery_user_add_unread_message_count(user_id):
    print(1)
    this_user = User.objects.get(id=user_id)
    unread_message_count = this_user.unread_message_count
    this_user.unread_message_count = unread_message_count + 1
    this_user.save()
    print('celery_user_add_unread_message_count')
