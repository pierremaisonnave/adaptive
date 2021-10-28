from django.contrib.auth.models import AbstractUser
from django.db import models
from django_resized import ResizedImageField

class User(AbstractUser):
    role=models.CharField(max_length=20,choices=(('WRITER','WRITER'),('READER','READER'),('VALIDATOR','VALIDATOR'),('ADMINISTRATOR','ADMINISTRATOR')), default='WRITER')
    profile_picture = ResizedImageField(size=[150, 100],upload_to='profile_picture/',null=True,blank=True)#, default='royalty_app/static/default.png'
    pass

class Payment_type(models.Model):
    payment_type = models.CharField(max_length=50)
    def __str__(self):
        return f"{self.payment_type} "

class Region(models.Model):
    region = models.CharField(max_length=50)
    def __str__(self):
        return f"{self.region} "

class Country(models.Model):
    country_id = models.CharField(max_length=10, primary_key=True)
    country = models.CharField(max_length=100)
    country_region= models.ForeignKey(Region, related_name="country_region",on_delete=models.PROTECT)
    def __str__(self):
        return f"{self.country_id}"

class Type(models.Model):
    name=  models.CharField(max_length=50)
    def __str__(self):
        return f"{self.name}" 

class Partner(models.Model):
    partner_name = models.CharField(max_length=100)
    partner_m3_code=models.CharField(max_length=50,null=True,blank=True)
    partner_country= models.ForeignKey(Country, related_name="partner_country",on_delete=models.PROTECT)
    partner_bank_account = models.CharField(max_length=100,null=True,blank=True)
    partner_payment_type=models.ForeignKey(Payment_type, related_name="partner_payment_type",on_delete=models.PROTECT)
    ico_3rd=models.CharField(max_length=3,choices=(('3rd','3rd'),('ICO','ICO')), default='3rd')
    partner_proposal= models.ForeignKey('self',null=True,on_delete=models.CASCADE,blank=True)
    status=models.CharField(max_length=20,choices=(('CHANGE','CHANGE'),('PROPOSAL','PROPOSAL'),('NEW','NEW'),('DELETE','DELETE'),('CURRENT','CURRENT')), default='NEW')
    def __str__(self):
        return f"{self.partner_name}"

class Accounting(models.Model):
    contract_type=  models.ForeignKey(Type, related_name="accounting_type",on_delete=models.PROTECT)
    transaction_direction= models.CharField(max_length=3,choices=(('PAY','PAY'),('REC','REC')), default='PAY')
    account_nb= models.CharField(max_length=20,null=True,blank=True)
    cost_center_acc= models.CharField(max_length=20,null=True,blank=True)
    market_acc= models.CharField(max_length=20,null=True,blank=True)
    pl_bs= models.CharField(max_length=2,choices=(('PL','PL'),('BS','BS')), default='PL')
    d_c_if_amount_positiv= models.CharField(max_length=1,choices=(('D','D'),('C','C')), default='C')

class Brand(models.Model):
    brand_code= models.CharField(max_length=20)
    brand_name= models.CharField(max_length=50)
    def __str__(self):
        return f"{self.brand_name}"

class Formulation(models.Model):
    formula_code= models.CharField(max_length=20, primary_key=True)
    formula_name= models.CharField(max_length=200)
    def __str__(self):
        return f"{self.formula_code}"

class Currency(models.Model):
    currency= models.CharField(max_length=10, primary_key=True)
    def __str__(self):
        return f"{self.currency}"

class Division(models.Model):
    division_id= models.CharField(max_length=20 , primary_key=True)
    division_name= models.CharField(max_length=50)
    division_country=models.ForeignKey(Country, on_delete=models.PROTECT)
    def __str__(self):
        return f"{self.division_id}"

class Tax(models.Model):
    country_from=  models.ForeignKey(Country, related_name="country_from",on_delete=models.PROTECT)
    country_to=  models.ForeignKey(Country, related_name="country_to",on_delete=models.PROTECT)
    wht_rate= models.DecimalField( max_digits=5, decimal_places=2)


class Periodicity(models.Model):
    periodicity= models.CharField(max_length=20)
    def __str__(self):
        return f"{self.periodicity}"

class Month_table(models.Model):
    month_nb=models.IntegerField( primary_key=True)
    month_name= models.CharField(max_length=20)
    def __str__(self):
        return f"{self.month_name}"

class Periodicity_cat(models.Model):
    periodicity_cat= models.CharField(max_length=20)
    periodicity= models.ForeignKey(Periodicity, related_name="periodicity_structure",on_delete=models.PROTECT)
    period_month_end= models.ForeignKey(Month_table, related_name="month_periodicity_structure",on_delete=models.PROTECT)
    def __str__(self):
        return f"{self.periodicity}:{self.periodicity_cat}"

class Payment_structure(models.Model):
    sales_month= models.ForeignKey(Month_table, related_name="month_payment_structure",on_delete=models.PROTECT)
    periodicity_cat= models.ForeignKey(Periodicity_cat, related_name="periodicity_cat_structure",on_delete=models.PROTECT)

class Consolidation_currency(models.Model):
    currency=  models.ForeignKey(Currency,on_delete=models.PROTECT)
    def __str__(self):
        return f"{self.currency}"     

class Contract(models.Model):
    contract_name= models.CharField(max_length=50)
    contract_type=  models.ForeignKey(Type, related_name="type",on_delete=models.PROTECT)
    transaction_direction=models.CharField(max_length=3,choices=(('PAY','PAY'),('REC','REC')), default='PAY')
    division=  models.ForeignKey(Division, related_name="contract_division",on_delete=models.PROTECT)
    division_via=  models.ForeignKey(Division, related_name="contract_division_via",on_delete=models.SET_NULL,null=True,blank=True)
    contract_currency=  models.ForeignKey(Currency, related_name="contract_currency",on_delete=models.PROTECT)
    payment_periodicity=  models.ForeignKey(Periodicity, related_name="payment_periodicity",on_delete=models.PROTECT)
    payment_terms= models.IntegerField()
    m3_brand=  models.ForeignKey(Brand, related_name="m3_brand",on_delete=models.PROTECT)
    mini_gar_status=models.CharField(max_length=3,choices=(('YES','YES'),('NO','NO')), default='NO')
    mini_gar_from=models.IntegerField(default=1900)
    mini_gar_to=models.IntegerField(default=2100)
    minimum_guar_amount=models.IntegerField(null=True,blank=True)
    minimum_guar_remaining_allocation_country= models.ForeignKey(Country, related_name="minimum_guar_remaining_allocation_country",on_delete=models.SET_NULL,null=True,blank=True)
    contract_proposal= models.ForeignKey('self',null=True,on_delete=models.CASCADE,blank=True)
    status=models.CharField(max_length=20,choices=(('IN_CREATION','IN_CREATION'),('CHANGE','CHANGE'),('PROPOSAL','PROPOSAL'),('NEW','NEW'),('DELETE','DELETE'),('CURRENT','CURRENT')), default='IN_CREATION')
    def __str__(self):
        return f"{self.contract_name}"

class Contract_file(models.Model):
    name = models.CharField(max_length=255)
    contract=  models.ForeignKey(Contract,on_delete=models.CASCADE)
    upload = models.FileField(upload_to='contracts/')



class Contract_partner(models.Model):
    contract=  models.ForeignKey(Contract,on_delete=models.CASCADE)
    partner=  models.ForeignKey(Partner,on_delete=models.PROTECT)
    percentage= models.FloatField()

class Rule(models.Model):
    contract=  models.ForeignKey(Contract, related_name="rule_contract",on_delete=models.CASCADE)
    rule_type=models.CharField(max_length=20,choices=(('SALES','SALES'),('COGS','COGS'),('ROYALTY','ROYALTY'),('MARGIN','MARGIN')), default='ROYALTY')
    formulation=models.ManyToManyField(Formulation, related_name="rule_formulation")
    country_incl_excl=models.CharField(max_length=7,choices=(('EXCLUDE','EXCLUDE'),('INCLUDE','INCLUDE')), default='INCLUDE')
    country=models.ManyToManyField(Country, related_name="rule_country",blank=True)
    country_list=models.CharField(max_length=10000,null=True,blank=True)
    field_type=models.CharField(max_length=7,choices=(('RATE','RATE'),('QTY','QTY')), default='RATE')
    period_from=models.DateField(default="1900-01-01")
    period_to=models.DateField(default="2100-01-01")
    tranche_type=models.CharField(max_length=7,choices=(('YES','YES'),('NO','NO')), default='NO')
    rate_value=models.FloatField(null=True,blank=True)
    qty_value=models.FloatField(null=True,blank=True)
    tranche_currency=models.ForeignKey(Currency, related_name="rule_tranche_currency", on_delete=models.PROTECT, default="USD")
    qty_value_currency=models.ForeignKey(Currency,on_delete=models.PROTECT, default="USD" ,related_name="qty_value_currency")
    def __str__(self):
        return f"{self.id}"

class Milestone(models.Model):
    contract=  models.ForeignKey(Contract, related_name="milestone_contract",on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    amount=models.FloatField(default=0)
    currency=models.ForeignKey(Currency, related_name="milestone_currency", on_delete=models.PROTECT, default="USD")
    booked=models.CharField(max_length=3,choices=(('YES','YES'),('NO','NO')), default='NO')
    market=models.ForeignKey(Country, related_name="market_milestone",on_delete=models.PROTECT, default="USA")
    booking_date=models.DateField(default="1900-01-01")
    payment_date=models.DateField(default="1900-01-01")
    def __str__(self):
        return f"{self.id}"
    
class Tranche(models.Model):
    rule=  models.ForeignKey(Rule, related_name="tranche_rule",on_delete=models.CASCADE)
    from_amount=models.FloatField(null=True,blank=True)
    to_amount=models.FloatField(null=True,blank=True)
    percentage=models.FloatField(null=True,blank=True)
    def __str__(self):
        return f"{self.rule}"

class Invoice(models.Model):
    contract=  models.ForeignKey(Contract, related_name="invoice_contract",on_delete=models.PROTECT)
    partner=  models.ForeignKey(Partner, related_name="invoice_partner",on_delete=models.PROTECT)
    amount=models.FloatField(default=0)
    currency=  models.ForeignKey(Currency, related_name="invoice_currency",on_delete=models.PROTECT)
    booking_date=models.DateField(default="1900-01-01")
    year=  models.IntegerField()
    periodicity_cat=  models.ForeignKey(Periodicity_cat, related_name="invoice_periodicity_cat",on_delete=models.PROTECT)
    comment= models.CharField(max_length=50,null=True,blank=True)
    paid=models.BooleanField(default=False)
    market=models.ForeignKey(Country, related_name="invoice_market",on_delete=models.PROTECT,null=True)
    def __str__(self):
        return f"{self.id}"

class File(models.Model):
    name= models.CharField(max_length=50,null=True,blank=True)
    date=models.DateTimeField(auto_now=True)
    acc_month= models.ForeignKey(Month_table, related_name="acc_month_file",on_delete=models.PROTECT)
    acc_year= models.IntegerField()
    dashboard= models.BooleanField(default=False)
    file_type=models.CharField(max_length=20,choices=(('accruals','accruals'),('cash_forecast','cash_forecast'),('partner_report','partner_report')), default='accruals')
    def __str__(self):
        return f"{self.name}"

class Sale(models.Model):
    import_file=models.ForeignKey(File, on_delete=models.CASCADE)
    year= models.IntegerField(null=True,blank=True)
    month=models.IntegerField(null=True,blank=True)
    country_id= models.CharField(max_length=10,null=True,blank=True)
    SKU= models.CharField(max_length=10,null=True,blank=True)
    SKU_name= models.CharField(max_length=100,null=True,blank=True)
    formulation=models.CharField(max_length=50)
    volume=models.BigIntegerField(null=True,blank=True)
    sales=models.FloatField(null=True,blank=True)
    sales_currency= models.CharField(max_length=10,null=True,blank=True)

class Fx(models.Model):
    import_file=models.ForeignKey(File, on_delete=models.CASCADE)
    year= models.IntegerField()
    currency= models.CharField(max_length=10,null=True,blank=True)
    exchange_rate=models.FloatField(null=True,blank=True)

class Rule_calc(models.Model):
    import_file=models.ForeignKey(File, on_delete=models.CASCADE)
    contract_id= models.CharField(max_length=100,null=True,blank=True)
    year= models.IntegerField(null=True,blank=True)
    contract_name= models.CharField(max_length=100,null=True,blank=True)
    country_incl_excl= models.CharField(max_length=100,null=True,blank=True)
    country_list= models.CharField(max_length=2000,null=True,blank=True)
    formulation= models.CharField(max_length=50,null=True,blank=True)
    period_from=models.DateField(default="1900-01-01")
    period_to= models.DateField(default="1900-01-01")
    tranche_type= models.CharField(max_length=3,null=True,blank=True)
    field_type= models.CharField(max_length=10,null=True,blank=True)
    qty_value= models.CharField(max_length=100,null=True,blank=True)
    sales_rate= models.FloatField(null=True,blank=True)

class Conso(models.Model):
    import_file=models.ForeignKey(File, on_delete=models.CASCADE)
    year_of_sales=models.IntegerField()
    division= models.CharField(max_length=10,null=True,blank=True)
    brand_name= models.CharField(max_length=100,null=True,blank=True)
    country= models.CharField(max_length=100,null=True,blank=True)
    consolidation_currency= models.CharField(max_length=10,null=True,blank=True)
    amount_consolidation_curr= models.FloatField(null=True,blank=True)

class Accounting_entry(models.Model):
    import_file=models.ForeignKey(File, on_delete=models.CASCADE)
    contract_type=  models.ForeignKey(Type, related_name="contract_type_acc_entr",on_delete=models.PROTECT)
    sheet_name= models.CharField(max_length=100,null=True,blank=True)
    division= models.CharField(max_length=10,null=True,blank=True)
    contract_currency= models.CharField(max_length=10,null=True,blank=True)
    accountingdate= models.CharField(max_length=50,null=True,blank=True)
    reverseDate= models.CharField(max_length=50,null=True,blank=True)
    account_nb= models.CharField(max_length=50,null=True,blank=True)
    cost_center_acc= models.CharField(max_length=50,null=True,blank=True)
    brand_code= models.CharField(max_length=50,null=True,blank=True)
    market_acc= models.CharField(max_length=50,null=True,blank=True)
    accruals_contract_curr= models.FloatField(null=True,blank=True)
    d_c= models.CharField(max_length=10,null=True,blank=True)
    text_voucherline= models.CharField(max_length=100,null=True,blank=True)


class Detail(models.Model):
    rule_type=models.CharField(max_length=20,null=True,blank=True)
    import_file=models.ForeignKey(File, on_delete=models.CASCADE)
    division= models.CharField(max_length=10,null=True,blank=True)
    division_country_id= models.CharField(max_length=10,null=True,blank=True)
    division_via= models.CharField(max_length=10,null=True,blank=True)
    field_type= models.CharField(max_length=50,null=True,blank=True)
    year_of_sales= models.IntegerField(null=True,blank=True)
    month_of_sales= models.IntegerField(null=True,blank=True)
    SKU_name= models.CharField(max_length=100,null=True,blank=True)
    SKU= models.CharField(max_length=10,null=True,blank=True)    
    market_id= models.CharField(max_length=10,null=True,blank=True)
    sales_in_market_curr=models.FloatField(null=True,blank=True, default=0)
    sales_in_contract_curr=models.FloatField(null=True,blank=True, default=0)
    volume=models.FloatField(null=True,blank=True, default=0)
    market_curr= models.CharField(max_length=10,null=True,blank=True)
    sales_rate= models.FloatField(null=True,blank=True)
    qty_value= models.CharField(max_length=100,null=True,blank=True)
    beneficiary_percentage= models.FloatField(null=True,blank=True)
    amount_contract_curr= models.FloatField(null=True,blank=True)
    transaction_direction= models.CharField(max_length=10,null=True,blank=True)
    contract_currency= models.CharField(max_length=10,null=True,blank=True)
    amount_payment_curr= models.FloatField(null=True,blank=True)
    payment_currency= models.ForeignKey(Currency, on_delete=models.PROTECT)
    amount_consolidation_curr= models.FloatField(null=True,blank=True)
    consolidation_currency= models.CharField(max_length=10,null=True,blank=True)
    contract=models.ForeignKey(Contract, on_delete=models.PROTECT)
    contract_type=models.ForeignKey(Type, on_delete=models.PROTECT)
    contract_name= models.CharField(max_length=100,null=True,blank=True)
    partner=models.ForeignKey(Partner, on_delete=models.PROTECT)
    ico_3rd= models.CharField(max_length=3,null=True,blank=True)
    partner_name= models.CharField(max_length=100,null=True,blank=True)
    partner_country_id= models.CharField(max_length=10,null=True,blank=True)
    brand_name= models.CharField(max_length=100,null=True,blank=True)
    brand_code= models.CharField(max_length=100,null=True,blank=True)
    period= models.CharField(max_length=100,null=True,blank=True)
    invoice_paid= models.CharField(max_length=10,null=True,blank=True)
    invoice_detail= models.CharField(max_length=100,null=True,blank=True)
    payment_date= models.DateField(default="1900-01-01",null=True,blank=True)


class Cash_flow(models.Model):
    import_file=models.ForeignKey(File, on_delete=models.CASCADE)
    division= models.CharField(max_length=10,null=True,blank=True)
    rule_type= models.CharField(max_length=20,null=True,blank=True)
    invoice_paid= models.CharField(max_length=10,null=True,blank=True)
    transaction_direction= models.CharField(max_length=10,null=True,blank=True)
    #payment_currency= models.CharField(max_length=10,null=True,blank=True)
    payment_currency= models.ForeignKey(Currency, on_delete=models.PROTECT)
    payment_date= models.DateField(default="1900-01-01")
    amount_payment_curr= models.FloatField(null=True,blank=True)    

class Wht(models.Model):
    import_file=models.ForeignKey(File, on_delete=models.CASCADE)
    from_payor= models.CharField(max_length=100,null=True,blank=True)   
    to_payee= models.CharField(max_length=100,null=True,blank=True)   
    payment_currency= models.ForeignKey(Currency, on_delete=models.PROTECT)  
    amount_payment_curr= models.FloatField(null=True,blank=True) 
    wht_rate= models.CharField(max_length=100,null=True,blank=True)

class Sales_breakdown_item(models.Model):
    sales_breakdown_definition= models.CharField(max_length=50)
    def __str__(self):
        return f"{self.sales_breakdown_definition}"

class Sales_breakdown_per_contract(models.Model):
    contract=  models.ForeignKey(Contract, related_name="sales_breakdown_per_contract_contract",on_delete=models.CASCADE)
    sales_breakdown_item=  models.ForeignKey(Sales_breakdown_item,related_name="sales_breakdown_per_contract_item",on_delete=models.PROTECT)
    sales_breakdown_contract_definition= models.CharField(max_length=50)

class Sales_breakdown_for_contract_report(models.Model):
    import_file=models.ForeignKey(File, on_delete=models.CASCADE)
    contract_name= models.CharField(max_length=100,null=True,blank=True)
    year= models.IntegerField()
    month= models.IntegerField()
    country_id= models.CharField(max_length=10,null=True,blank=True)
    formulation= models.CharField(max_length=50,null=True,blank=True)
    SKU= models.CharField(max_length=10,null=True,blank=True)
    SKU_name= models.CharField(max_length=100,null=True,blank=True)   
    sales_currency= models.CharField(max_length=5,null=True,blank=True)  
    volume =models.FloatField(null=True,blank=True) 
    sales_breakdown_definition= models.CharField(max_length=100,null=True,blank=True) 
    sales_breakdown_contract_definition= models.CharField(max_length=100,null=True,blank=True) 
    contract_currency= models.CharField(max_length=5,null=True,blank=True) 
    sales_in_market_curr =models.FloatField(null=True,blank=True) 
    sales_in_contract_curr =models.FloatField(null=True,blank=True) 