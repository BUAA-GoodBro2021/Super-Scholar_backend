# Generated by Django 4.1.2 on 2022-12-05 12:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("comment", "0010_comment_work_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="commentofcomments",
            name="comment_id_list",
            field=models.TextField(default="[]", max_length=20000, verbose_name="评论id"),
        ),
        migrations.AlterField(
            model_name="commentofworks",
            name="comment_id_list",
            field=models.TextField(default="[]", max_length=20000, verbose_name="评论id"),
        ),
    ]
