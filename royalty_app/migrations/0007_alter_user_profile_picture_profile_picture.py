# Generated by Django 3.2 on 2021-07-17 15:41

from django.db import migrations
import django_resized.forms


class Migration(migrations.Migration):

    dependencies = [
        ('royalty_app', '0006_alter_user_profile_picture_profile_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user_profile_picture',
            name='profile_picture',
            field=django_resized.forms.ResizedImageField(crop=None, default='royalty_app/static/default.png', force_format=None, keep_meta=True, quality=0, size=[150, 100], upload_to='profile_picture/'),
        ),
    ]
