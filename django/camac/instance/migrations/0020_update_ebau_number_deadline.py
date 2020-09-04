# Generated by Django 2.2.13 on 2020-07-28 14:29

from datetime import timedelta

from django.db import migrations
from django.db.models import F
from django.conf import settings


def update_ebau_number_deadline(apps, schema_editor):
    if settings.APPLICATION_NAME != "kt_bern":
        return

    WorkItem = apps.get_model("caluma_workflow", "WorkItem")

    WorkItem.objects.filter(task_id="ebau-number").update(
        deadline=F("created_at") + timedelta(days=5)
    )


class Migration(migrations.Migration):
    dependencies = [("instance", "0019_create_historyentry")]

    operations = [
        migrations.RunPython(update_ebau_number_deadline, migrations.RunPython.noop)
    ]
