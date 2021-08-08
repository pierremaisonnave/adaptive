# Generated by Django 3.2 on 2021-08-08 15:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('royalty_app', '0004_detail_rule_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rule',
            name='report_currency',
            field=models.ForeignKey(default='USD', on_delete=django.db.models.deletion.PROTECT, related_name='tranche_currency_rule', to='royalty_app.currency'),
        ),
    ]
