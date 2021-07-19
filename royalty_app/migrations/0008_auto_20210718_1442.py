# Generated by Django 3.2 on 2021-07-18 12:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('royalty_app', '0007_alter_user_profile_picture_profile_picture'),
    ]

    operations = [
        migrations.AddField(
            model_name='rule_calc',
            name='year_rule',
            field=models.CharField(blank=True, max_length=6, null=True),
        ),
        migrations.AlterField(
            model_name='contract_file',
            name='upload',
            field=models.FileField(upload_to='contracts/'),
        ),
    ]
