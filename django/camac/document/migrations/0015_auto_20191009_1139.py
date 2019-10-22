# -*- coding: utf-8 -*-
# Generated by Django 1.11.22 on 2019-10-09 09:39
from __future__ import unicode_literals

import uuid

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0014_auto_20190710_1326'),
    ]

    operations = [
        migrations.AddField(
            model_name='attachment',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, null=True),
        ),
        migrations.AlterField(
            model_name='attachment',
            name='digital_signature',
            field=models.PositiveSmallIntegerField(db_column='DIGITAL_SIGNATURE', default=0, validators=[django.core.validators.MaxValueValidator(1)]),
        ),
        migrations.AlterField(
            model_name='attachment',
            name='is_confidential',
            field=models.PositiveSmallIntegerField(db_column='IS_CONFIDENTIAL', default=0, validators=[django.core.validators.MaxValueValidator(1)]),
        ),
        migrations.AlterField(
            model_name='attachment',
            name='is_parcel_picture',
            field=models.PositiveIntegerField(db_column='IS_PARCEL_PICTURE', default=0, validators=[django.core.validators.MaxValueValidator(1)]),
        ),
    ]