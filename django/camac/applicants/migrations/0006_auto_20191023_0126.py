# -*- coding: utf-8 -*-
# Generated by Django 1.11.22 on 2019-10-22 23:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('applicants', '0005_auto_20190923_1006'),
    ]

    operations = [
        migrations.AlterField(
            model_name='applicant',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
    ]
