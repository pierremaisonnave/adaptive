from django.urls import path
from . import views


urlpatterns = [
  # /

  path('', views.home, name='home'),
  path("login", views.login_page, name="login"),
  path("login_view", views.login_view, name="login_view"),
  path("register", views.register, name="register"),

  path("logout", views.logout_view, name="logout"),
  path("new_profile_pict", views.new_profile_pict, name="new_profile_pict"),
  #pages
  path('account/', views.accountSettings, name="account"),

  path('partners', views.partners, name='partners'),
  path('contracts', views.contracts, name='contracts'),
  path('contracts/<int:contract_id>', views.rules, name='rules'),
  path('analytics', views.analytics, name='analytics'),
  path('invoices', views.invoices, name='invoices'),

  path('settings', views.settings, name='settings'),
  path('partner_report', views.partner_report, name='partner_report'),

  #reports
  path('monthly_accruals', views.monthly_accruals, name='monthly_accruals'),
  path('cash_flow_forecast', views.cash_flow_forecast, name='cash_flow_forecast'),  

  #static data static_data
  path('static_data', views.static_data, name='static_data'),
  path("static_data/<str:table_name>", views.modif_static, name="modif_static"),
  #-----------------------------------------------------
  #                        API
  #-----------------------------------------------------
  #static_file
  path('export/<str:file>', views.export, name='export'), 


  #Partner
  path("change_row/<int:partner_id>", views.change_row, name="change_row"),
  path("cancel_row_partner/<int:partner_id>", views.cancel_row_partner, name="cancel_row_partner"),
  path("delete_row_partner/<int:partner_id>", views.delete_row_partner, name="delete_row_partner"),
  path("new_partner", views.new_partner, name="new_partner"),
  
  #Contracts
  path("cancel_row_contract/<int:contract_id>", views.cancel_row_contract, name="cancel_row_contract"),
  path("change_row_contract/<int:contract_id>", views.change_row_contract, name="change_row_contract"),
  path("new_contract", views.new_contract, name="new_contract"),
  path("delete_row_contract/<int:contract_id>", views.delete_row_contract, name="delete_row_contract"),
  

  #Rule :  contract_partner + formula/country/rate rules + contract breakdown
  path("save_contract_partner/<int:contract_id>", views.save_contract_partner, name="save_contract_partner"),
  path("save_rule/<int:contract_id>", views.save_rule, name="save_rule"),
  path("save_invoice_breakdown/<int:contract_id>", views.save_invoice_breakdown, name="save_invoice_breakdown"),
  path("new_contract_file", views.new_contract_file, name="new_contract_file"),
  path("delete_contract_file/<int:cf_id>", views.delete_contract_file, name="delete_contract_file"),

  # invoice
  path("new_invoice", views.new_invoice, name="new_invoice"),
  path("save_paid_status", views.save_paid_status, name="save_paid_status"),
  path("delete_row_invoice/<int:invoice_id>", views.delete_row_invoice, name="delete_row_invoice"),
  
  # Accrual and Cash Forecast
  path("new_report", views.new_report, name="new_report"),
  path("save_dashboard", views.save_dashboard, name="save_dashboard"),
  path("delete_row_file/<int:file_id>", views.delete_row_file, name="delete_row_file"),
  path("export_report/files:<str:file_array>/tables:<str:table_array>", views.export_report, name="export_report"),
  
  #save static
  path("save_division", views.save_division, name="save_division"),
  path("save_country", views.save_country, name="save_country"),
  path("save_region", views.save_region, name="save_region"),
  path("save_brand", views.save_brand, name="save_brand"),
  path("save_formulation", views.save_formulation, name="save_formulation"),
  path("save_currency", views.save_currency, name="save_currency"),
  path("save_consolidation_currency", views.save_consolidation_currency, name="save_consolidation_currency"),
  path("save_accounting", views.save_accounting, name="save_accounting"),
  path("save_tax", views.save_tax, name="save_tax"),
  path("save_sales_breakdown_item", views.save_sales_breakdown_item, name="save_sales_breakdown_item"),
  path("save_payment_type", views.save_payment_type, name="save_payment_type"),
  #Home
  path("accruals_change", views.accruals_change, name="accruals_change"),
  path("cash_forecast_change", views.cash_forecast_change, name="cash_forecast_change"),
  
  #-----------------------------------------------------



  #-----------------------------------------------------
  
]