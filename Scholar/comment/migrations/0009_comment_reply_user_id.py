# Generated by Django 4.1.2 on 2022-11-21 11:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("comment", "0008_rename_comnentofworks_commentofworks"),
    ]

    operations = [
        migrations.AddField(
            model_name="comment",
            name="reply_user_id",
            field=models.IntegerField(default=0, verbose_name="回复评论的用户id"),
        ),
    ]