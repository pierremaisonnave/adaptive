# Generated by Django 3.2 on 2021-07-13 09:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('royalty_app', '0003_alter_user_profile_picture_profile_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user_profile_picture',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
