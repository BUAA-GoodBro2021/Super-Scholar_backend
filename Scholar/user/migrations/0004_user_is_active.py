# Generated by Django 4.1 on 2022-10-22 17:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0003_alter_user_introduction"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="is_active",
            field=models.BooleanField(default=False, verbose_name="邮箱是否验证"),
        ),
    ]
