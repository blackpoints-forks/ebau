# Generated by Django 2.2.13 on 2020-06-22 13:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0061_merge_20200618_0826'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activation',
            name='reason',
            field=models.CharField(blank=True, db_column='REASON', max_length=4000, null=True),
        ),
    ]