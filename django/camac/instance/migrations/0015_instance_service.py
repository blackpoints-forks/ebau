# -*- coding: utf-8 -*-
# Generated by Django 1.11.22 on 2019-09-10 07:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0007_rename_duplicated_users'),
        ('core', '0038_buildingauthorityemail_attachment_section'),
        ('instance', '0014_unify_instance_states_sb1_sb2'),
    ]

    operations = [
        migrations.AddField(
            model_name='instance',
            name='services',
            field=models.ManyToManyField(through='core.InstanceService', to='user.Service'),
        ),
    ]