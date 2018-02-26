# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-02-23 10:09
from __future__ import unicode_literals

from django.conf import settings
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('user', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Form',
            fields=[
                ('form_id', models.AutoField(db_column='FORM_ID', primary_key=True, serialize=False)),
                ('name', models.CharField(db_column='NAME', max_length=500)),
                ('description', models.CharField(blank=True, db_column='DESCRIPTION', max_length=1000, null=True)),
            ],
            options={
                'db_table': 'FORM',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='FormField',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=500)),
                ('value', django.contrib.postgres.fields.jsonb.JSONField()),
            ],
        ),
        migrations.CreateModel(
            name='FormState',
            fields=[
                ('form_state_id', models.AutoField(db_column='FORM_STATE_ID', primary_key=True, serialize=False)),
                ('name', models.CharField(db_column='NAME', max_length=50)),
            ],
            options={
                'db_table': 'FORM_STATE',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Instance',
            fields=[
                ('instance_id', models.AutoField(db_column='INSTANCE_ID', primary_key=True, serialize=False)),
                ('creation_date', models.DateTimeField(db_column='CREATION_DATE')),
                ('modification_date', models.DateTimeField(db_column='MODIFICATION_DATE')),
                ('form', models.ForeignKey(db_column='FORM_ID', on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='instance.Form')),
                ('group', models.ForeignKey(db_column='GROUP_ID', on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='user.Group')),
            ],
            options={
                'db_table': 'INSTANCE',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='InstanceState',
            fields=[
                ('instance_state_id', models.AutoField(db_column='INSTANCE_STATE_ID', primary_key=True, serialize=False)),
                ('name', models.CharField(db_column='NAME', max_length=100)),
                ('sort', models.IntegerField(db_column='SORT')),
            ],
            options={
                'db_table': 'INSTANCE_STATE',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='InstanceStateDescription',
            fields=[
                ('instance_state', models.OneToOneField(db_column='INSTANCE_STATE_ID', on_delete=django.db.models.deletion.DO_NOTHING, primary_key=True, related_name='description', serialize=False, to='instance.InstanceState')),
                ('description', models.CharField(db_column='DESCRIPTION', max_length=255)),
            ],
            options={
                'db_table': 'INSTANCE_STATE_DESCRIPTION',
                'managed': True,
            },
        ),
        migrations.AddField(
            model_name='instance',
            name='instance_state',
            field=models.ForeignKey(db_column='INSTANCE_STATE_ID', on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='instance.InstanceState'),
        ),
        migrations.AddField(
            model_name='instance',
            name='locations',
            field=models.ManyToManyField(blank=True, db_table='INSTANCE_LOCATION', to='user.Location'),
        ),
        migrations.AddField(
            model_name='instance',
            name='previous_instance_state',
            field=models.ForeignKey(db_column='PREVIOUS_INSTANCE_STATE_ID', on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='instance.InstanceState'),
        ),
        migrations.AddField(
            model_name='instance',
            name='user',
            field=models.ForeignKey(db_column='USER_ID', on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='formfield',
            name='instance',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fields', to='instance.Instance'),
        ),
        migrations.AddField(
            model_name='form',
            name='form_state',
            field=models.ForeignKey(db_column='FORM_STATE_ID', on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='instance.FormState'),
        ),
        migrations.AlterUniqueTogether(
            name='formfield',
            unique_together=set([('instance', 'name')]),
        ),
    ]
