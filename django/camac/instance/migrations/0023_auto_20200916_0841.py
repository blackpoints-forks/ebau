# Generated by Django 2.2.16 on 2020-09-16 06:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('instance', '0022_skip_circulation'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""update caluma_workflow_workitem set meta = jsonb_set(meta, '{notify-completed}', 'false'::jsonb) where meta->'notify-completed' = 'true';""",
        ),
    ]
