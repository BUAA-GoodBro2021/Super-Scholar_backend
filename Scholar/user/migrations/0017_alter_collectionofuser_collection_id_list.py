# Generated by Django 4.1.2 on 2022-12-03 20:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0016_user_institution_user_institution_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="collectionofuser",
            name="collection_id_list",
            field=models.TextField(
                default="[]", max_length=20000, verbose_name="用户收藏夹的id列表"
            ),
        ),
    ]
