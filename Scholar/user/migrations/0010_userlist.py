# Generated by Django 4.0.4 on 2022-11-25 17:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0009_followofuser'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_list', models.TextField(default='[]', max_length=1024, verbose_name='用户的id的列表')),
            ],
        ),
    ]
