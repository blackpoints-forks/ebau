# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-06-05 08:46
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('document', '0011_attachment_meta'),
    ]

    operations = [
        migrations.RenameField(
            model_name='attachment',
            old_name='meta',
            new_name='context',
        ),
    ]
