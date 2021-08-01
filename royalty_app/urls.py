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

 #change user role- API, onl valid in test mode:
  path("change_role", views.change_role, name="change_role"),
 


  #---------------------Partner-------------------------------
  #------------------------------------------------------------
  path('partners/writer', views.partners_writer, name='partners'),
  path('partners/to_validate', views.partners_to_validate, name='partners_to_validate'),
  path('partners/current', views.partners_current, name='partners_current'),
  path('validate_new_partner/<int:partner_id>', views.validate_new_partner, name='validate_new_partner'),
  path('validate_change_partner/<int:partner_id>', views.validate_change_partner, name='validate_change_partner'),
  path('reject_change_partner/<int:partner_id>', views.reject_change_partner, name='reject_change_partner'),
  path('delete_partner/<int:partner_id>', views.delete_partner, name='delete_partner'),
  path("new_partner", views.new_partner, name="new_partner"),

  #-------------------Contract (and rules)---------------------
  #------------------------------------------------------------
  # related to summary of contracts 
  path('contracts/writer', views.contracts_writer, name='contracts_writer'),
  path('contracts/to_validate', views.contracts_to_validate, name='contracts_to_validate'),
  path('contracts/current', views.contracts_current, name='contracts_current'),
  path('contracts/writer/<int:contract_id>', views.rules_writer, name='rules_writer'),
  path('contracts/to_validate/<int:contract_id>', views.rules_validator, name='rules_validator'),
  path('contracts/current/<int:contract_id>', views.rules_current, name='rules_current'),
  path('delete_contract/<int:contract_id>', views.delete_contract, name='delete_contract'),
  path('submit_delete_contract_request/<int:contract_id>', views.submit_delete_contract_request, name='submit_delete_contract_request'),
  path("change_row/<int:partner_id>", views.change_row, name="change_row"),
  path("cancel_row_partner/<int:partner_id>", views.cancel_row_partner, name="cancel_row_partner"),
  path("delete_row_partner/<int:partner_id>", views.delete_row_partner, name="delete_row_partner"),

  path("cancel_row_contract/<int:contract_id>", views.cancel_row_contract, name="cancel_row_contract"),
  path("change_row_contract/<int:contract_id>", views.change_row_contract, name="change_row_contract"),
  path("new_contract", views.new_contract, name="new_contract"),
  path("delete_row_contract/<int:contract_id>", views.delete_row_contract, name="delete_row_contract"),
 # Modification/creation of a specific contract 
  path("save_contract_partner/<int:contract_id>", views.save_contract_partner, name="save_contract_partner"),
  path("save_mini/<int:contract_id>", views.save_mini, name="save_mini"),
  path("save_rule/<int:contract_id>", views.save_rule, name="save_rule"),
  path("save_invoice_breakdown/<int:contract_id>", views.save_invoice_breakdown, name="save_invoice_breakdown"),
  path("new_contract_file", views.new_contract_file, name="new_contract_file"),
  path("save_contract_basic_info/<int:contract_id>/<str:save_type>", views.save_contract_basic_info, name="save_contract_basic_info"),
  path("pdf_file_to_keep/<int:contract_id>", views.pdf_file_to_keep, name="pdf_file_to_keep"),
  #API response_validator
  path("response_validator", views.response_validator, name="response_validator"),


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