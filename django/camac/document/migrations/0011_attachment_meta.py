# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-05-23 12:52
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0010_attachmentdownloadhistory'),
    ]

    operations = [
        migrations.AddField(
            model_name='attachment',
            name='meta',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=dict),
        ),
    ]
