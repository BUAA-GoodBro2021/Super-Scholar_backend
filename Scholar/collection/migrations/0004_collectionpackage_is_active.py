# Generated by Django 4.1.2 on 2022-11-02 00:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("collection", "0003_remove_collection_user_id_alter_collection_work_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="collectionpackage",
            name="is_active",
            field=models.BooleanField(default=True, verbose_name="是否删除"),
        ),
    ]
