# Generated by Django 4.0.4 on 2022-11-03 20:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('author', '0004_remove_author_id_alter_author_user_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='author',
            name='is_pass',
            field=models.IntegerField(default=0, verbose_name='是否通过'),
        ),
    ]