# Generated by Django 3.2 on 2021-08-08 15:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('royalty_app', '0006_alter_rule_report_currency'),
    ]

    operations = [
        migrations.RenameField(
            model_name='rule',
            old_name='report_currency',
            new_name='tranche_currency',
        ),
    ]
