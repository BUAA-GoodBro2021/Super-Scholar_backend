# Generated by Django 4.1.2 on 2022-11-04 19:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("comment", "0002_alter_comment_content_alter_comment_father_id_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="ComnentOfWorks",
            fields=[
                (
                    "work_id",
                    models.CharField(
                        default="",
                        max_length=200,
                        primary_key=True,
                        serialize=False,
                        verbose_name="评论文章的id",
                    ),
                ),
                (
                    "comment_id_list",
                    models.TextField(default="", max_length=20000, verbose_name="评论id"),
                ),
            ],
            options={"db_table": "scholar_comment_of_works",},
        ),
        migrations.AlterField(
            model_name="comment",
            name="work_id",
            field=models.CharField(default="", max_length=200, verbose_name="评论文章的id"),
        ),
    ]
