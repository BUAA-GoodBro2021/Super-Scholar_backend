# Generated by Django 4.0.4 on 2022-11-03 19:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('form', '0002_alter_form_content_alter_form_user_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='form',
            name='author_id',
            field=models.CharField(default='', max_length=200, verbose_name='对应的open_alex_id'),
        ),
    ]
