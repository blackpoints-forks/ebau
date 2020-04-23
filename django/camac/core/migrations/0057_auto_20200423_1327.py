# Generated by Django 2.2.11 on 2020-04-23 11:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0056_auto_20200408_1507'),
    ]

    operations = [
        migrations.AddField(
            model_name='archive',
            name='workflow_item',
            field=models.ForeignKey(db_column='WORKFLOW_ITEM_ID', default=87, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='core.WorkflowItem'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='buildingauthorityemail',
            name='workflow_item',
            field=models.ForeignKey(blank=True, db_column='WORKFLOW_ITEM_ID', null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='core.WorkflowItem'),
        ),
    ]
