# Generated by Django 2.2.14 on 2020-08-31 12:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [("core", "0074_auto_20200828_1719")]

    operations = [
        migrations.CreateModel(
            name="ActionCase",
            fields=[
                (
                    "action",
                    models.OneToOneField(
                        db_column="ACTION_ID",
                        on_delete=django.db.models.deletion.CASCADE,
                        primary_key=True,
                        related_name="+",
                        serialize=False,
                        to="core.Action",
                    ),
                ),
                (
                    "process_type",
                    models.CharField(
                        choices=[
                            ("cancel", "cancel"),
                            ("suspend", "suspend"),
                            ("resume", "resume"),
                        ],
                        db_column="PROCESS_TYPE",
                        max_length=10,
                    ),
                ),
            ],
            options={"db_table": "ACTION_CASE", "managed": True},
        )
    ]