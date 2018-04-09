# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-04-09 11:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0002_auto_20180308_1038'),
    ]

    operations = [
        migrations.AlterField(
            model_name='template',
            name='id',
            field=models.AutoField(db_column='ID', primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='template',
            name='name',
            field=models.CharField(db_column='NAME', max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='template',
            name='path',
            field=models.FileField(db_column='PATH', max_length=1024, upload_to='templates'),
        ),
        migrations.AlterModelTable(
            name='template',
            table='TEMPLATE',
        ),
    ]
