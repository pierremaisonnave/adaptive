# Generated by Django 3.2 on 2021-07-11 17:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('royalty_app', '0003_alter_file_acc_year'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='year',
            field=models.IntegerField(),
        ),
    ]
