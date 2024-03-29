# Generated by Django 4.0.6 on 2022-10-21 12:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('collection', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collectionpackage',
            name='name',
            field=models.CharField(default='默认收藏夹', max_length=50, verbose_name='收藏夹的名字'),
        ),
        migrations.AlterField(
            model_name='collectionpackage',
            name='sum',
            field=models.IntegerField(default=0, verbose_name='收藏夹的收藏数目'),
        ),
        migrations.AlterField(
            model_name='collectionpackage',
            name='user_id',
            field=models.IntegerField(default=0, verbose_name='对应用户的id'),
        ),
    ]
