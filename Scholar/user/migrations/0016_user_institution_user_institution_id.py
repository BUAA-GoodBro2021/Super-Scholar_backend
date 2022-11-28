# Generated by Django 4.0.4 on 2022-11-28 22:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0015_merge_20221128_1806'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='institution',
            field=models.CharField(db_index=True, default='', max_length=200, null=True, verbose_name='作者的机构'),
        ),
        migrations.AddField(
            model_name='user',
            name='institution_id',
            field=models.CharField(db_index=True, default='', max_length=200, null=True, verbose_name='作者的机构的open_alex_id'),
        ),
    ]
