# Generated by Django 3.2 on 2022-03-29 11:03

import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import django_resized.forms


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Brand',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('brand_code', models.CharField(max_length=20)),
                ('brand_name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Contract',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contract_name', models.CharField(max_length=50)),
                ('transaction_direction', models.CharField(choices=[('PAY', 'PAY'), ('REC', 'REC')], default='PAY', max_length=3)),
                ('payment_terms', models.IntegerField()),
                ('mini_gar_status', models.CharField(choices=[('YES', 'YES'), ('NO', 'NO')], default='NO', max_length=3)),
                ('mini_gar_from', models.IntegerField(default=1900)),
                ('mini_gar_to', models.IntegerField(default=2100)),
                ('minimum_guar_amount', models.IntegerField(blank=True, null=True)),
                ('status', models.CharField(choices=[('IN_CREATION', 'IN_CREATION'), ('CHANGE', 'CHANGE'), ('PROPOSAL', 'PROPOSAL'), ('NEW', 'NEW'), ('DELETE', 'DELETE'), ('CURRENT', 'CURRENT')], default='IN_CREATION', max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('country_id', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('country', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('currency', models.CharField(max_length=10, primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=50, null=True)),
                ('date', models.DateTimeField(auto_now=True)),
                ('acc_year', models.IntegerField()),
                ('dashboard', models.BooleanField(default=False)),
                ('file_type', models.CharField(choices=[('accruals', 'accruals'), ('cash_forecast', 'cash_forecast'), ('partner_report', 'partner_report')], default='accruals', max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Formulation',
            fields=[
                ('formula_code', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('formula_name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Month_table',
            fields=[
                ('month_nb', models.IntegerField(primary_key=True, serialize=False)),
                ('month_name', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Payment_type',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_type', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Periodicity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('periodicity', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('region', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Rule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rule_type', models.CharField(choices=[('SALES', 'SALES'), ('COGS', 'COGS'), ('ROYALTY', 'ROYALTY'), ('MARGIN', 'MARGIN')], default='ROYALTY', max_length=20)),
                ('country_incl_excl', models.CharField(choices=[('EXCLUDE', 'EXCLUDE'), ('INCLUDE', 'INCLUDE')], default='INCLUDE', max_length=7)),
                ('country_list', models.CharField(blank=True, max_length=10000, null=True)),
                ('field_type', models.CharField(choices=[('RATE', 'RATE'), ('QTY', 'QTY')], default='RATE', max_length=7)),
                ('period_from', models.DateField(default='1900-01-01')),
                ('period_to', models.DateField(default='2100-01-01')),
                ('tranche_type', models.CharField(choices=[('YES', 'YES'), ('NO', 'NO')], default='NO', max_length=7)),
                ('rate_value', models.FloatField(blank=True, null=True)),
                ('qty_value', models.FloatField(blank=True, null=True)),
                ('contract', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rule_contract', to='royalty_app.contract')),
                ('country', models.ManyToManyField(blank=True, related_name='rule_country', to='royalty_app.Country')),
                ('formulation', models.ManyToManyField(related_name='rule_formulation', to='royalty_app.Formulation')),
                ('qty_value_currency', models.ForeignKey(default='USD', on_delete=django.db.models.deletion.PROTECT, related_name='qty_value_currency', to='royalty_app.currency')),
                ('tranche_currency', models.ForeignKey(default='USD', on_delete=django.db.models.deletion.PROTECT, related_name='rule_tranche_currency', to='royalty_app.currency')),
            ],
        ),
        migrations.CreateModel(
            name='Sales_breakdown_item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sales_breakdown_definition', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Type',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Wht',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('from_payor', models.CharField(blank=True, max_length=100, null=True)),
                ('to_payee', models.CharField(blank=True, max_length=100, null=True)),
                ('amount_payment_curr', models.FloatField(blank=True, null=True)),
                ('wht_rate', models.CharField(blank=True, max_length=100, null=True)),
                ('import_file', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='royalty_app.file')),
                ('payment_currency', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='royalty_app.currency')),
            ],
        ),
        migrations.CreateModel(
            name='Tranche',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('from_amount', models.FloatField(blank=True, null=True)),
                ('to_amount', models.FloatField(blank=True, null=True)),
                ('percentage', models.FloatField(blank=True, null=True)),
                ('rule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tranche_rule', to='royalty_app.rule')),
            ],
        ),
        migrations.CreateModel(
            name='Tax',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('wht_rate', models.DecimalField(decimal_places=2, max_digits=5)),
                ('country_from', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='country_from', to='royalty_app.country')),
                ('country_to', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='country_to', to='royalty_app.country')),
            ],
        ),
        migrations.CreateModel(
            name='Sales_breakdown_per_contract',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sales_breakdown_contract_definition', models.CharField(max_length=50)),
                ('contract', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sales_breakdown_per_contract_contract', to='royalty_app.contract')),
                ('sales_breakdown_item', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='sales_breakdown_per_contract_item', to='royalty_app.sales_breakdown_item')),
            ],
        ),
        migrations.CreateModel(
            name='Sales_breakdown_for_contract_report',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contract_name', models.CharField(blank=True, max_length=100, null=True)),
                ('year', models.IntegerField()),
                ('month', models.IntegerField()),
                ('country_id', models.CharField(blank=True, max_length=10, null=True)),
                ('formulation', models.CharField(blank=True, max_length=50, null=True)),
                ('SKU', models.CharField(blank=True, max_length=10, null=True)),
                ('SKU_name', models.CharField(blank=True, max_length=100, null=True)),
                ('sales_currency', models.CharField(blank=True, max_length=5, null=True)),
                ('volume', models.FloatField(blank=True, null=True)),
                ('sales_breakdown_definition', models.CharField(blank=True, max_length=100, null=True)),
                ('sales_breakdown_contract_definition', models.CharField(blank=True, max_length=100, null=True)),
                ('contract_currency', models.CharField(blank=True, max_length=5, null=True)),
                ('sales_in_market_curr', models.FloatField(blank=True, null=True)),
                ('sales_in_contract_curr', models.FloatField(blank=True, null=True)),
                ('import_file', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='royalty_app.file')),
            ],
        ),
        migrations.CreateModel(
            name='Sale',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField(blank=True, null=True)),
                ('month', models.IntegerField(blank=True, null=True)),
                ('country_id', models.CharField(blank=True, max_length=10, null=True)),
                ('SKU', models.CharField(blank=True, max_length=10, null=True)),
                ('SKU_name', models.CharField(blank=True, max_length=100, null=True)),
                ('formulation', models.CharField(max_length=50)),
                ('volume', models.BigIntegerField(blank=True, null=True)),
                ('sales', models.FloatField(blank=True, null=True)),
                ('sales_currency', models.CharField(blank=True, max_length=10, null=True)),
                ('import_file', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='royalty_app.file')),
            ],
        ),
        migrations.CreateModel(
            name='Rule_calc',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contract_id', models.CharField(blank=True, max_length=100, null=True)),
                ('year', models.IntegerField(blank=True, null=True)),
                ('contract_name', models.CharField(blank=True, max_length=100, null=True)),
                ('country_incl_excl', models.CharField(blank=True, max_length=100, null=True)),
                ('country_list', models.CharField(blank=True, max_length=2000, null=True)),
                ('formulation', models.CharField(blank=True, max_length=50, null=True)),
                ('period_from', models.DateField(default='1900-01-01')),
                ('period_to', models.DateField(default='1900-01-01')),
                ('tranche_type', models.CharField(blank=True, max_length=3, null=True)),
                ('field_type', models.CharField(blank=True, max_length=10, null=True)),
                ('qty_value', models.CharField(blank=True, max_length=100, null=True)),
                ('sales_rate', models.FloatField(blank=True, null=True)),
                ('import_file', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='royalty_app.file')),
            ],
        ),
        migrations.CreateModel(
            name='Periodicity_cat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('periodicity_cat', models.CharField(max_length=20)),
                ('period_month_end', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='month_periodicity_structure', to='royalty_app.month_table')),
                ('periodicity', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='periodicity_structure', to='royalty_app.periodicity')),
            ],
        ),
        migrations.CreateModel(
            name='Payment_structure',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('periodicity_cat', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='periodicity_cat_structure', to='royalty_app.periodicity_cat')),
                ('sales_month', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='month_payment_structure', to='royalty_app.month_table')),
            ],
        ),
        migrations.CreateModel(
            name='Partner',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('partner_name', models.CharField(max_length=100)),
                ('partner_m3_code', models.CharField(blank=True, max_length=50, null=True)),
                ('partner_bank_account', models.CharField(blank=True, max_length=100, null=True)),
                ('ico_3rd', models.CharField(choices=[('3rd', '3rd'), ('ICO', 'ICO')], default='3rd', max_length=3)),
                ('status', models.CharField(choices=[('CHANGE', 'CHANGE'), ('PROPOSAL', 'PROPOSAL'), ('NEW', 'NEW'), ('DELETE', 'DELETE'), ('CURRENT', 'CURRENT')], default='NEW', max_length=20)),
                ('partner_country', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='partner_country', to='royalty_app.country')),
                ('partner_payment_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='partner_payment_type', to='royalty_app.payment_type')),
                ('partner_proposal', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='royalty_app.partner')),
            ],
        ),
        migrations.CreateModel(
            name='Milestone',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('amount', models.FloatField(default=0)),
                ('booked', models.CharField(choices=[('YES', 'YES'), ('NO', 'NO')], default='NO', max_length=3)),
                ('booking_date', models.DateField(default='1900-01-01')),
                ('payment_date', models.DateField(default='1900-01-01')),
                ('contract', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='milestone_contract', to='royalty_app.contract')),
                ('currency', models.ForeignKey(default='USD', on_delete=django.db.models.deletion.PROTECT, related_name='milestone_currency', to='royalty_app.currency')),
                ('market', models.ForeignKey(default='USA', on_delete=django.db.models.deletion.PROTECT, related_name='market_milestone', to='royalty_app.country')),
            ],
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.FloatField(default=0)),
                ('booking_date', models.DateField(default='1900-01-01')),
                ('year', models.IntegerField()),
                ('comment', models.CharField(blank=True, max_length=50, null=True)),
                ('paid', models.BooleanField(default=False)),
                ('contract', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='invoice_contract', to='royalty_app.contract')),
                ('currency', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='invoice_currency', to='royalty_app.currency')),
                ('market', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='invoice_market', to='royalty_app.country')),
                ('partner', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='invoice_partner', to='royalty_app.partner')),
                ('periodicity_cat', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='invoice_periodicity_cat', to='royalty_app.periodicity_cat')),
            ],
        ),
        migrations.CreateModel(
            name='Fx',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField()),
                ('currency', models.CharField(blank=True, max_length=10, null=True)),
                ('exchange_rate', models.FloatField(blank=True, null=True)),
                ('import_file', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='royalty_app.file')),
            ],
        ),
        migrations.AddField(
            model_name='file',
            name='acc_month',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='acc_month_file', to='royalty_app.month_table'),
        ),
        migrations.CreateModel(
            name='Division',
            fields=[
                ('division_id', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('division_name', models.CharField(max_length=50)),
                ('division_country', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='royalty_app.country')),
            ],
        ),
        migrations.CreateModel(
            name='Detail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rule_type', models.CharField(blank=True, max_length=20, null=True)),
                ('division', models.CharField(blank=True, max_length=10, null=True)),
                ('division_country_id', models.CharField(blank=True, max_length=10, null=True)),
                ('division_via', models.CharField(blank=True, max_length=10, null=True)),
                ('field_type', models.CharField(blank=True, max_length=50, null=True)),
                ('year_of_sales', models.IntegerField(blank=True, null=True)),
                ('month_of_sales', models.IntegerField(blank=True, null=True)),
                ('SKU_name', models.CharField(blank=True, max_length=100, null=True)),
                ('SKU', models.CharField(blank=True, max_length=10, null=True)),
                ('market_id', models.CharField(blank=True, max_length=10, null=True)),
                ('sales_in_market_curr', models.FloatField(blank=True, default=0, null=True)),
                ('sales_in_contract_curr', models.FloatField(blank=True, default=0, null=True)),
                ('volume', models.FloatField(blank=True, default=0, null=True)),
                ('market_curr', models.CharField(blank=True, max_length=10, null=True)),
                ('sales_rate', models.FloatField(blank=True, null=True)),
                ('qty_value', models.CharField(blank=True, max_length=100, null=True)),
                ('beneficiary_percentage', models.FloatField(blank=True, null=True)),
                ('amount_contract_curr', models.FloatField(blank=True, null=True)),
                ('transaction_direction', models.CharField(blank=True, max_length=10, null=True)),
                ('contract_currency', models.CharField(blank=True, max_length=10, null=True)),
                ('amount_payment_curr', models.FloatField(blank=True, null=True)),
                ('amount_consolidation_curr', models.FloatField(blank=True, null=True)),
                ('consolidation_currency', models.CharField(blank=True, max_length=10, null=True)),
                ('contract_name', models.CharField(blank=True, max_length=100, null=True)),
                ('ico_3rd', models.CharField(blank=True, max_length=3, null=True)),
                ('partner_name', models.CharField(blank=True, max_length=100, null=True)),
                ('partner_country_id', models.CharField(blank=True, max_length=10, null=True)),
                ('brand_name', models.CharField(blank=True, max_length=100, null=True)),
                ('brand_code', models.CharField(blank=True, max_length=100, null=True)),
                ('period', models.CharField(blank=True, max_length=100, null=True)),
                ('invoice_paid', models.CharField(blank=True, max_length=10, null=True)),
                ('invoice_detail', models.CharField(blank=True, max_length=100, null=True)),
                ('payment_date', models.DateField(blank=True, default='1900-01-01', null=True)),
                ('contract', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='royalty_app.contract')),
                ('contract_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='royalty_app.type')),
                ('import_file', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='royalty_app.file')),
                ('partner', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='royalty_app.partner')),
                ('payment_currency', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='royalty_app.currency')),
            ],
        ),
        migrations.AddField(
            model_name='country',
            name='country_region',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='country_region', to='royalty_app.region'),
        ),
        migrations.CreateModel(
            name='Contract_partner',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('percentage', models.FloatField()),
                ('contract', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='royalty_app.contract')),
                ('partner', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='royalty_app.partner')),
            ],
        ),
        migrations.CreateModel(
            name='Contract_file',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('upload', models.FileField(upload_to='contracts/')),
                ('contract', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='royalty_app.contract')),
            ],
        ),
        migrations.AddField(
            model_name='contract',
            name='contract_currency',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='contract_currency', to='royalty_app.currency'),
        ),
        migrations.AddField(
            model_name='contract',
            name='contract_proposal',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='royalty_app.contract'),
        ),
        migrations.AddField(
            model_name='contract',
            name='contract_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='type', to='royalty_app.type'),
        ),
        migrations.AddField(
            model_name='contract',
            name='division',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='contract_division', to='royalty_app.division'),
        ),
        migrations.AddField(
            model_name='contract',
            name='division_via',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='contract_division_via', to='royalty_app.division'),
        ),
        migrations.AddField(
            model_name='contract',
            name='m3_brand',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='m3_brand', to='royalty_app.brand'),
        ),
        migrations.AddField(
            model_name='contract',
            name='minimum_guar_remaining_allocation_country',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='minimum_guar_remaining_allocation_country', to='royalty_app.country'),
        ),
        migrations.AddField(
            model_name='contract',
            name='payment_periodicity',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='payment_periodicity', to='royalty_app.periodicity'),
        ),
        migrations.CreateModel(
            name='Consolidation_currency',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('currency', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='royalty_app.currency')),
            ],
        ),
        migrations.CreateModel(
            name='Conso',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year_of_sales', models.IntegerField()),
                ('division', models.CharField(blank=True, max_length=10, null=True)),
                ('brand_name', models.CharField(blank=True, max_length=100, null=True)),
                ('country', models.CharField(blank=True, max_length=100, null=True)),
                ('consolidation_currency', models.CharField(blank=True, max_length=10, null=True)),
                ('amount_consolidation_curr', models.FloatField(blank=True, null=True)),
                ('import_file', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='royalty_app.file')),
            ],
        ),
        migrations.CreateModel(
            name='Cash_flow',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('division', models.CharField(blank=True, max_length=10, null=True)),
                ('rule_type', models.CharField(blank=True, max_length=20, null=True)),
                ('invoice_paid', models.CharField(blank=True, max_length=10, null=True)),
                ('transaction_direction', models.CharField(blank=True, max_length=10, null=True)),
                ('payment_date', models.DateField(default='1900-01-01')),
                ('amount_payment_curr', models.FloatField(blank=True, null=True)),
                ('import_file', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='royalty_app.file')),
                ('payment_currency', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='royalty_app.currency')),
            ],
        ),
        migrations.CreateModel(
            name='Accounting_entry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sheet_name', models.CharField(blank=True, max_length=100, null=True)),
                ('division', models.CharField(blank=True, max_length=10, null=True)),
                ('contract_currency', models.CharField(blank=True, max_length=10, null=True)),
                ('accountingdate', models.CharField(blank=True, max_length=50, null=True)),
                ('reverseDate', models.CharField(blank=True, max_length=50, null=True)),
                ('account_nb', models.CharField(blank=True, max_length=50, null=True)),
                ('cost_center_acc', models.CharField(blank=True, max_length=50, null=True)),
                ('brand_code', models.CharField(blank=True, max_length=50, null=True)),
                ('market_acc', models.CharField(blank=True, max_length=50, null=True)),
                ('accruals_contract_curr', models.FloatField(blank=True, null=True)),
                ('d_c', models.CharField(blank=True, max_length=10, null=True)),
                ('text_voucherline', models.CharField(blank=True, max_length=100, null=True)),
                ('contract_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='contract_type_acc_entr', to='royalty_app.type')),
                ('import_file', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='royalty_app.file')),
            ],
        ),
        migrations.CreateModel(
            name='Accounting',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_direction', models.CharField(choices=[('PAY', 'PAY'), ('REC', 'REC')], default='PAY', max_length=3)),
                ('account_nb', models.CharField(blank=True, max_length=20, null=True)),
                ('cost_center_acc', models.CharField(blank=True, max_length=20, null=True)),
                ('market_acc', models.CharField(blank=True, max_length=20, null=True)),
                ('pl_bs', models.CharField(choices=[('PL', 'PL'), ('BS', 'BS')], default='PL', max_length=2)),
                ('d_c_if_amount_positiv', models.CharField(choices=[('D', 'D'), ('C', 'C')], default='C', max_length=1)),
                ('contract_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='accounting_type', to='royalty_app.type')),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('role', models.CharField(choices=[('WRITER', 'WRITER'), ('READER', 'READER'), ('VALIDATOR', 'VALIDATOR'), ('ADMINISTRATOR', 'ADMINISTRATOR')], default='WRITER', max_length=20)),
                ('profile_picture', django_resized.forms.ResizedImageField(blank=True, crop=None, force_format=None, keep_meta=True, null=True, quality=0, size=[150, 100], upload_to='profile_picture/')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
