# Generated by Django 4.0.4 on 2022-11-27 15:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('form', '0011_rename_form_list_formlist_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='form',
            name='institution',
            field=models.CharField(default='', max_length=200, verbose_name='机构名称'),
        ),
        migrations.AddField(
            model_name='form',
            name='real_name',
            field=models.CharField(default='', max_length=200, verbose_name='真名'),
        ),
    ]
