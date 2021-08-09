from django.contrib import admin
from .models import (Invoice,Country,Region,Partner,
    Payment_type,Accounting,Brand,Formulation,Currency,
    Division,Tax,Periodicity,Payment_structure,Contract,
    Contract_partner,Rule,Tranche,Periodicity_cat,
    File,Sale,Fx,Rule_calc,Conso,Accounting_entry,Consolidation_currency,
    Detail,Wht,Sales_breakdown_for_contract_report,Sales_breakdown_per_contract,
    Contract_file,Month_table,User,Type)






# Register your models here.
class CountryAdmin(admin.ModelAdmin):
    list_display = ("country_id", "country","country_region")

class RegionAdmin(admin.ModelAdmin):
    list_display = ("pk","region")

class Payment_typeAdmin(admin.ModelAdmin):
    list_display = ("pk","payment_type")

class PartnerAdmin(admin.ModelAdmin):
    list_display = ("partner_name","partner_m3_code","partner_country","partner_payment_type")

class AccountingAdmin(admin.ModelAdmin):
    list_display = ("transaction_direction","dim1","dim2","market_acc","pl_bs","d_c_if_amount_positiv")

class BrandAdmin(admin.ModelAdmin):
    list_display = ("id","m3_brand_code","brand_name")

class FormulationAdmin(admin.ModelAdmin):
    list_display = ("formula_code","formula_name")

class DivisionAdmin(admin.ModelAdmin):
    list_display = ("division_id","division_name","division_country")

class TaxAdmin(admin.ModelAdmin):
    list_display = ("country_from","country_to","wht_rate")

class Payment_structureAdmin(admin.ModelAdmin):
    list_display = ("sales_month","periodicity_cat")

class ContractAdmin(admin.ModelAdmin):
    list_display = ("contract_name","transaction_direction","division","division_via","contract_currency","payment_periodicity","payment_terms","m3_brand","mini_gar_status","minimum_guar_amount","minimum_guar_remaining_allocation_country")

class Contract_partnerAdmin(admin.ModelAdmin):
    list_display=("id","contract","partner","percentage")

class Tranche_partnerAdmin(admin.ModelAdmin):
    list_display=("rule","id","from_amount","to_amount","percentage")

class Periodicity_catAdmin(admin.ModelAdmin):
    list_display=("periodicity","periodicity_cat","period_month_end")

class InvoiceAdmin(admin.ModelAdmin):
    list_display=("contract","partner","amount","year","periodicity_cat","comment","paid")

class FileAdmin(admin.ModelAdmin):
    list_display=("name","date","acc_month","acc_year")

class SaleAdmin(admin.ModelAdmin):
    list_display=("import_file","year","month","country_id","formulation","volume","sales","sales_currency")

class FxAdmin(admin.ModelAdmin):
    list_display=("import_file","year","currency","exchange_rate")

class RuleAdmin(admin.ModelAdmin):
    list_display=("contract","country_incl_excl","country_list","field_type","period_from","period_to","rate_value","qty_value","tranche_currency")

class Rule_calcAdmin(admin.ModelAdmin):
    list_display=("import_file","contract_id","country_incl_excl","country_list","formulation","period_from","period_to","tranche_type","field_type","qty_value","sales_rate")

class Sales_breakdown_per_contractAdmin(admin.ModelAdmin):
    list_display=("contract","sales_breakdown_item","sales_breakdown_contract_definition")

class Contract_fileAdmin(admin.ModelAdmin):
    list_display=("name","contract")



admin.site.register(Country, CountryAdmin)
admin.site.register(Region,RegionAdmin)
admin.site.register(Payment_type,Payment_typeAdmin)
admin.site.register(Partner,PartnerAdmin)
admin.site.register(Accounting,AccountingAdmin)
admin.site.register(Brand,BrandAdmin)
admin.site.register(Formulation,FormulationAdmin)
admin.site.register(Division,DivisionAdmin)
admin.site.register(Tax,TaxAdmin)
admin.site.register(Periodicity)
admin.site.register(Payment_structure,Payment_structureAdmin)
admin.site.register(Contract,ContractAdmin)
admin.site.register(Currency)
admin.site.register(Contract_partner,Contract_partnerAdmin)
admin.site.register(Rule,RuleAdmin)
admin.site.register(Tranche,Tranche_partnerAdmin)
admin.site.register(Periodicity_cat,Periodicity_catAdmin)
admin.site.register(Invoice,InvoiceAdmin)
admin.site.register(File,FileAdmin)
admin.site.register(Sale,SaleAdmin)
admin.site.register(Fx,FxAdmin)
admin.site.register(Rule_calc,Rule_calcAdmin)
admin.site.register(Conso)
admin.site.register(Accounting_entry)
admin.site.register(Consolidation_currency)
admin.site.register(Detail)
admin.site.register(Wht)
admin.site.register(Contract_file,Contract_fileAdmin)
admin.site.register(Sales_breakdown_per_contract,Sales_breakdown_per_contractAdmin)
admin.site.register(Sales_breakdown_for_contract_report)
admin.site.register(Month_table)
admin.site.register(User)
admin.site.register(Type)

