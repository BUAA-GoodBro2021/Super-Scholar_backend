# Generated by Django 4.1.2 on 2022-11-27 18:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("work", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="work",
            name="work_name",
            field=models.CharField(
                db_index=True, default="", max_length=200, verbose_name="论文的名字"
            ),
        ),
    ]
