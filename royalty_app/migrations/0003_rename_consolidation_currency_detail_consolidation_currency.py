# Generated by Django 3.2 on 2021-07-25 08:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('royalty_app', '0002_auto_20210725_1040'),
    ]

    operations = [
        migrations.RenameField(
            model_name='detail',
            old_name='Consolidation_currency',
            new_name='consolidation_currency',
        ),
    ]
