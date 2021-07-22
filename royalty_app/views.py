from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from datetime import datetime, timedelta
from pandas.tseries.offsets import MonthEnd
from django.http import JsonResponse
from .models import (Invoice,Country,Partner,Region,Payment_type,Brand,
  Accounting,Formulation,Currency,Division,Tax,Periodicity,
  Payment_structure,Contract,Contract_partner,Rule,Tranche,
  Periodicity_cat,Fx,Sales_breakdown_item,Sales_breakdown_per_contract,Sales_breakdown_item,
  File,Sale, Rule_calc,Periodicity_cat,Consolidation_currency,Cash_flow,Detail,Gls,Conso,Wht,Sales_breakdown_for_contract_report,
  Contract_file,Month_table,User,User_profile_picture)
from django.views.decorators.csrf import csrf_exempt
import pandas as pd
import numpy as np
import json
import sqlite3
from io import BytesIO
from django.db.models import ProtectedError
import django_excel as excel
import pyexcel as p

from django.contrib.auth import authenticate, login , logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.contrib.auth import password_validation

# bunch of import used to send confirmatrion email
from django.shortcuts import render
from django.contrib.auth import get_user_model
from django_email_verification import send_email




def login_view(request):
    if request.method == "POST":
        #check if user is active:
        username = request.POST["username"]
        password = request.POST["password"]
        # Attempt to sign user in
        active_user=User.objects.filter(username=username)
        if active_user :
          user=get_user_model().objects.get(username=username)
          error_message=[]
          if user.is_active == False:
            error_message.append(f"your email has not been verified yet- another token was sent to {username}")
            error_message.append("If your token expired, or you did not receive the email, please contact your administrator")
            send_email(user)
            return render(request, "royalty_app/login.html", {
              "error_message": error_message
            })
            
        user = authenticate(request, username=username, password=password)
        # Check if authentication successful
        if user is not None:
          print(user.last_login) # if None, then it's a first time user, I should redirect him to a welcome page
          login(request, user)
          redirect=request.POST.get('next')
          if redirect=="":
            redirect="/"
          
          return HttpResponseRedirect(redirect) 
          # If the user clicked on "Partner", and if he is not logged in, he is automatically redirected t
          #..on the loggin page thanks to the "login_required", the login page keeps tracks of the original URL
          #i.e. "/login?next=/partners"- In order for the user to be directed on the "Partner" page rigth after entering the password
          #we must utilise request.POST.get('next')

        else:
          return render(request, "royalty_app/login.html", {
              "error_message": ['Invalid username and/or password.']
          })
    else:
        return render(request, "royalty_app/login.html")

def login_page(request):
  return render(request, "royalty_app/login.html")

@csrf_exempt
@login_required
def new_profile_pict(request):
  if request.method == "POST":
    try:
      if User_profile_picture.objects.filter(user=request.user):
        user_profile_picture=User_profile_picture.objects.get(user=request.user)
        user_profile_picture.profile_picture=request.FILES.get("file")

        user_profile_picture.save()
      else:  
        user_profile_picture=User_profile_picture(
          user =request.user,
          profile_picture=request.FILES.get("file"),
        )

        user_profile_picture.save()
      return JsonResponse({"new_picture_url":user_profile_picture.profile_picture.url}, status=201)
    except Exception as e:
      return JsonResponse({"error": f"data not loaded-   server message: {e}"}, status=404)



def register_page(request):

  return render(request, "royalty_app/register.html")


from royalty.settings.base import  GOOGLE_RECAPTCHA_SITE_KEY,GOOGLE_RECAPTCHA_SECRET_KEY
import requests
def register(request):

  if request.method == "POST":
        #---- captcha -----#
    recaptcha_response = request.POST.get('g-recaptcha-response')    
    data = {
        'secret': GOOGLE_RECAPTCHA_SECRET_KEY,
        'response': recaptcha_response
    }
    r = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
    result = r.json()
    #---- process data  -----#
    if result['success']: # if captcha is successful 

      username = request.POST["email"]
      email = request.POST["email"]
      first_name = request.POST["first_name"]
      last_name = request.POST["last_name"]

      # Ensure password matches confirmation
      password = request.POST["password"]
      confirmation = request.POST["confirmation"]
      if password != confirmation:
          return render(request, "royalty_app/register.html", {
              "error_message": ["Passwords must match."],'recaptcha_site_key':GOOGLE_RECAPTCHA_SITE_KEY
          })
      if User.objects.filter(email=email):
          return render(request, "royalty_app/register.html", {
              "error_message": ["Email already exists"],'recaptcha_site_key':GOOGLE_RECAPTCHA_SITE_KEY
          })
      try: 
        password_validation.validate_password(password, request)
      except Exception as e:
        return render(request, "royalty_app/register.html",{
          "error_message":e ,'recaptcha_site_key':GOOGLE_RECAPTCHA_SITE_KEY}
          )
      # Attempt to create new user
      try:
        user = User.objects.create_user(username, email, password)
        #user = get_user_model().objects.create(username=username, password=password, email=email)
        user.first_name=first_name
        user.last_name=last_name
        user.is_active = False
        user.save()
        send_email(user)
        pass#return HttpResponseRedirect(reverse("login"))     
      except IntegrityError:
        return render(request, "royalty_app/register.html", {
            "error_message": ["Username already taken"],'recaptcha_site_key':GOOGLE_RECAPTCHA_SITE_KEY
        })
      return render(request, "royalty_app/login.html", {"message_confirmation": "email for confimation has been sent"})
    else:
      return render(request, "royalty_app/register.html",{'recaptcha_site_key':GOOGLE_RECAPTCHA_SITE_KEY,"error_message": ["CAPTCHA must be validated"]})
  else:
    return render(request, "royalty_app/register.html",{'recaptcha_site_key':GOOGLE_RECAPTCHA_SITE_KEY})



@login_required
def logout_view(request):
  logout(request)
  return HttpResponseRedirect(reverse("home"))    


from .forms import  CustomerForm
@login_required
def accountSettings(request):
  print(request.user)
  customer = request.user.user_profile_picture
  form = CustomerForm(instance=customer)

  if request.method == 'POST':
    form = CustomerForm(request.POST, request.FILES,instance=customer)
    if form.is_valid():
      form.save()


  context = {'form':form}
  return render(request, 'royalty_app/account.html', context)



@login_required(login_url='/login')
def home(request):

    #---------------calculation for Accruals graph------------
    current_year=datetime.now().year
    year_list=File.objects.filter(file_type="accruals").values_list('acc_year')
    year_list=list(dict.fromkeys(year_list))
    year_list=[int(y[0]) for y in year_list]
    #if the current year does not exist, insert it in the list
    if current_year not in year_list:
      year_list.append(current_year)
    year_list.sort()

    consolidation_currency=Consolidation_currency.objects.all().first()
    contract_list=Contract.objects.all()
    contract_id_list=contract_list.values_list('id')
    contract_id_list=[c[0] for c in contract_id_list]


    result=chart_accruals(current_year,contract_id_list)
    labels=result[0]
    data_accruals=result[1]
    data_roy_ytd=result[2]

    result=chart_accruals(current_year-1,contract_id_list)
    data_accruals_last_year=result[1]
    data_roy_ytd_last_year=result[2]

  #---------------calculation for CFF graph------------
    CFF_report_list=File.objects.filter(file_type="cash_forecast").order_by('-id')[:30]
    #Get the list of cash flow report, and select the latest
    if not CFF_report_list :
      CFF_report_id=0
      year_list_cash_forecast=[current_year]
    else:
      CFF_report=CFF_report_list.first()
      CFF_report_id=CFF_report.id
      

    #get the currency list from the contract
    currency_list=contract_list.values_list('contract_currency')
    currency_list=list(dict.fromkeys(currency_list))
    currency_list=[str(c[0]) for c in currency_list]
    
    #get the label, data as well as the
    result=chart_cash_forecast(CFF_report_id,currency_list,current_year)
    labels_cash_forecast=result[0]
    data_cash_forecast=result[1] 
    year_list_cash_forecast=result[2]

    result=chart_cash_forecast(CFF_report_id,currency_list,current_year-1)
    data_cash_forecast_last_year=result[1] 

    return render(request, 'royalty_app/home.html', {"CFF_report_list":CFF_report_list,"CFF_report_id":CFF_report_id,"currency_list":currency_list,"year_list_cash_forecast":year_list_cash_forecast,"data_cash_forecast_last_year":data_cash_forecast_last_year,"data_cash_forecast":data_cash_forecast,"labels_cash_forecast":labels_cash_forecast,"data_accruals_last_year":data_accruals_last_year,"data_roy_ytd_last_year":data_roy_ytd_last_year,"contract_id_list":contract_id_list,"contract_list":contract_list,"consolidation_currency":consolidation_currency,"labels":labels,"data_accruals":data_accruals,"data_roy_ytd":data_roy_ytd,"year_list":year_list,"current_year":current_year})



@csrf_exempt
#@login_required
def chart_cash_forecast(CFF_report_id,currency_list,year):
  #get Year List
  current_year=datetime.now().year
  detail_list=Detail.objects.filter(import_file=CFF_report_id)
  year_list_cash_forecast=detail_list.values_list('payment_date')
  year_list_cash_forecast=pd.DataFrame.from_records(list(year_list_cash_forecast), columns=['payment_date'])
  year_list_cash_forecast["payment_date"]=pd.DatetimeIndex(year_list_cash_forecast["payment_date"]).year
  year_list_cash_forecast=year_list_cash_forecast.groupby(['payment_date'],as_index=False)
  year_list_cash_forecast=list(year_list_cash_forecast)
  year_list_cash_forecast=[y[0] for y in year_list_cash_forecast]
  if current_year not in year_list_cash_forecast:
    year_list_cash_forecast.append(current_year)
  year_list_cash_forecast.sort()

  #import detail tab:
  detail_list=Detail.objects.filter(import_file=CFF_report_id,contract_currency__in=currency_list,payment_date__year=year).values_list('payment_date','contract_currency','amount_consolidation_curr','entry_type','transaction_direction')
  df_detail_list=pd.DataFrame.from_records(list(detail_list), columns=['payment_date','contract_currency','amount_consolidation_curr','entry_type','transaction_direction'])


  if not detail_list :
    labels=[ "Jan", "Feb", "Mar", "Apr", "Mai", "Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    data=[0,0,0,0,0,0,0,0,0,0,0,0]
  else:
 
    df_data=df_detail_list.groupby(['payment_date','contract_currency','entry_type','transaction_direction'], as_index=False).agg({"amount_consolidation_curr": "sum"})

    df_data['payment_month'] =  pd.DatetimeIndex(df_data['payment_date']).month
    df_data['payment_month'] = df_data['payment_month'].astype(int)
    df_data=df_data.drop(['payment_date'], axis = 1)  


    df_data["amount"]=np.where(
      df_data["entry_type"]=="Invoice",
      0,
      df_data["amount_consolidation_curr"]
    )
    
    df_data["amount"]=np.where(
      df_data["transaction_direction"]=="REC",
      -df_data["amount"],
      df_data["amount"]
    )
    df_data["amount"]=df_data["amount"].round(decimals=0)
    df_month = pd.DataFrame({
      'month_nb': [1,2,3,4,5,6,7,8,9,10,11,12],
      'month': ["Jan", "Feb", "Mar", "Apr", "Mai", "Jun","Jul","Aug","Sep","Oct","Nov","Dec"],
    })


    df_data=pd.merge(df_month,df_data,how="left",left_on=["month_nb"],right_on=["payment_month"])
    
    df_data=df_data.groupby(['month_nb','month'], as_index=False,dropna=False).agg({"amount": "sum"})
    df_data=df_data.sort_values(['month_nb'], ascending=[1])
    df_data=df_data.drop(['month_nb'], axis = 1)
    df_data=df_data.fillna("0")


    datas=df_data.values.tolist()
    labels=[ d[0] for d in datas]
    data=[ d[1] for d in datas]
  return [labels, data,year_list_cash_forecast]




@csrf_exempt
@login_required
def accruals_change(request):
  if request.method == "POST":
    #Save File
    try:
      data = json.loads(request.body)

      year=int(data["year"])
      contract_list=data["contract_list"]
      if   contract_list ==['']:
        contract_list=["0"]

      result=chart_accruals(year,contract_list)
      data_accruals=result[1]
      data_roy_ytd=result[2] 

      result=chart_accruals(year-1,contract_list)
      data_accruals_last_year=result[1]
      data_roy_ytd_last_year=result[2] 
      
      return JsonResponse({"success": "data loaded","data_accruals_last_year":data_accruals_last_year,"data_roy_ytd_last_year":data_roy_ytd_last_year,"data_accruals":data_accruals,"data_roy_ytd":data_roy_ytd}, status=201)
    except Exception as e:
      return JsonResponse({"error": f"data not loaded-   server message: {e}"}, status=404)

@csrf_exempt
@login_required
def cash_forecast_change(request):
  if request.method == "POST":
    #Save File
    try:
      data = json.loads(request.body)

      year=int(data["year"])
      currency_list=data["currency_list"]
      if   currency_list ==['']:
        currency_list=["0"]

      CFF_report_id=data["CFF_report_id"]
      if   CFF_report_id =='':
        CFF_report_id=0
      
      result=chart_cash_forecast(CFF_report_id,currency_list,year)
      data_cash_forecast=result[1]
      year_list_cash_forecast=result[2]

      result=chart_cash_forecast(CFF_report_id,currency_list,year-1)
      data_cash_forecast_last_year=result[1] 


      return JsonResponse({"success": "data loaded","data_cash_forecast":data_cash_forecast,"data_cash_forecast_last_year":data_cash_forecast_last_year,"year_list_cash_forecast":year_list_cash_forecast,}, status=201)
    except Exception as e:
      return JsonResponse({"error": f"data not loaded-   server message: {e}"}, status=404)



#@login_required
def chart_accruals(year,contract_id_list):
  #-----------Default Chart JS-----------
  #create the list of available year

  file_list=File.objects.filter(file_type="accruals",acc_year=year,dashboard=True)
  df_file_list=pd.DataFrame(list(file_list.values()))
  if not file_list :
    labels=[ "Jan", "Feb", "Mar", "Apr", "Mai", "Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    data_accruals=[0,0,0,0,0,0,0,0,0,0,0,0]
    data_roy_ytd=[0,0,0,0,0,0,0,0,0,0,0,0]
  else:
    print("chart_accruals 1")
    #import detail tab:
    detail_list=Detail.objects.filter(import_file__in=file_list,contract_id__in=contract_id_list ).values_list('import_file_id','year_of_sales','amount_consolidation_curr','entry_type','transaction_direction')
    df_detail_list=pd.DataFrame.from_records(list(detail_list), columns=['import_file_id','year_of_sales','amount_consolidation_curr','entry_type','transaction_direction'])
    df_detail_list=df_detail_list.groupby(['import_file_id','year_of_sales','entry_type','transaction_direction'], as_index=False).agg({"amount_consolidation_curr": "sum"})
    print("chart_accruals 2")
    #merge file and detail:
    df_data=pd.merge(df_file_list,df_detail_list, how="inner",left_on=['id'], right_on=['import_file_id'] )
    #df_data=df_data.groupby(['acc_year','acc_month','entry_type','year_of_sales'], as_index=False).agg({"amount_consolidation_curr": "sum"})
    df_data["amount_consolidation_curr"]=df_data["amount_consolidation_curr"].round(decimals=0)   
    df_data["Accruals"]=np.where(
      df_data["entry_type"]=="Invoice",
      -df_data["amount_consolidation_curr"],
      df_data["amount_consolidation_curr"]
    )
    print("chart_accruals 3")
    df_data["Accruals"]=np.where(
      df_data["transaction_direction"]=="REC",
      -df_data["Accruals"],
      df_data["Accruals"]
    )
    print("chart_accruals 4")
    df_data["Ytd_roy"]=np.where(
      df_data["year_of_sales"]==df_data["acc_year"],
      np.where(
        df_data["entry_type"]=="Invoice",
        0,
        df_data["amount_consolidation_curr"]
      ),
      0
    )

    print("chart_accruals 5")
    df_data["Ytd_roy"]=np.where(
      df_data["transaction_direction"]=="REC",
      -df_data["Ytd_roy"],
      df_data["Ytd_roy"]
    )

    df_data=df_data.rename(columns={'acc_month_id':'acc_month'})
  
    df_month = pd.DataFrame({
      'month_nb': [1,2,3,4,5,6,7,8,9,10,11,12],
      'month': ["Jan", "Feb", "Mar", "Apr", "Mai", "Jun","Jul","Aug","Sep","Oct","Nov","Dec"],
    })
    print("chart_accruals 6")
    df_data=pd.merge(df_month,df_data,how="left",left_on=["month_nb"],right_on=["acc_month"])
    df_data["acc_year"]=year
    df_data=df_data.groupby(['acc_year','month_nb','month'], as_index=False,dropna=False).agg({"Accruals": "sum","Ytd_roy":"sum"})
    df_data=df_data.sort_values(['acc_year','month_nb'], ascending=[1,1])
    df_data=df_data.drop(['month_nb'], axis = 1)
    df_data=df_data.fillna("0")
    datas=df_data.values.tolist()

    labels=[ d[1] for d in datas]
    data_accruals=[ d[2] for d in datas]
    data_roy_ytd=[ d[3] for d in datas]
  return [labels, data_accruals,data_roy_ytd]
  #-----------------------------------
@login_required(login_url='/login')
def partners(request):
  partner_list=Partner.objects.all().select_related('partner_country','partner_payment_type')
  payment_type_list=Payment_type.objects.all()
  region_list=Region.objects.all()
  country_list=Country.objects.all().order_by("country").select_related('country_region')
  
  return render(request, 'royalty_app/partners.html',  { "payment_type_list":payment_type_list,"partner_list":partner_list, "country_list":country_list ,"region_list":region_list})

import time
@login_required(login_url='/login')
def contracts(request):


  contract_list=Contract.objects.all().select_related('m3_brand','division','division_via','payment_periodicity','minimum_guar_remaining_allocation_country','contract_currency')
  region_list=Region.objects.all()
  country_list=Country.objects.all().select_related('country_region')
  m3_brand_list=Brand.objects.all().order_by("brand_name")
  division_list=Division.objects.all()
  currency_list=Currency.objects.all()
  periodicity_list=Periodicity.objects.all()


  return render(request, 'royalty_app/contracts.html',  {"periodicity_list":periodicity_list,"currency_list":currency_list,"division_list":division_list,"m3_brand_list":m3_brand_list, "contract_list":contract_list,"region_list":region_list, "country_list":country_list})

@login_required(login_url='/login')
def rules(request,contract_id):

  contract=Contract.objects.get(id=contract_id)#.select_related('contract_currency')
  contract_file_list=Contract_file.objects.filter(contract=contract)
  contract_partner_list=Contract_partner.objects.filter(contract=contract)
  partner_list=Partner.objects.all().order_by("partner_name")
  country_list=Country.objects.all().order_by("country_id").select_related('country_region')
  region_list=Region.objects.all().order_by("region")
  formulation_list=Formulation.objects.all()
  currency_list=Currency.objects.all()
  rule_list=Rule.objects.filter(contract=contract)
  
  tranche_list=Tranche.objects.filter(rule__in=rule_list).order_by("id").select_related('rule')

  sbd=Sales_breakdown_item.objects.all()
  sbd_contract=Sales_breakdown_per_contract.objects.filter(contract=contract)
  sales_breakdown_list=[]
  for  item_sbd in sbd:
    sales_breakdown_contract_definition=""
    for item_sbd_contract in sbd_contract:
      if item_sbd_contract.sales_breakdown_item==item_sbd:
        sales_breakdown_contract_definition=item_sbd_contract.sales_breakdown_contract_definition
        break
    sub_dict={
      "id":item_sbd.id,
      "sales_breakdown_definition":item_sbd.sales_breakdown_definition,
      "sales_breakdown_contract_definition":sales_breakdown_contract_definition}
    sales_breakdown_list.append(sub_dict)  
      
  return render(request, 'royalty_app/rules.html', {"contract_file_list":contract_file_list,"sales_breakdown_list":sales_breakdown_list,"rule_list":rule_list,"currency_list":currency_list,"tranche_list":tranche_list,"formulation_list":formulation_list,"region_list":region_list,"country_list":country_list,"contract":contract,"contract_partner_list":contract_partner_list,"partner_list":partner_list})

@login_required(login_url='/login')
def analytics(request):
  return render(request, 'royalty_app/analytics.html', {})

@login_required(login_url='/login')
def invoices(request):
  contract_list=Contract.objects.all().order_by("contract_name").select_related('contract_currency','payment_periodicity')

  contract_partner_list=Contract_partner.objects.all().select_related('partner','contract')
  periodicity_cat_list=Periodicity_cat.objects.all().select_related('periodicity')
  invoice_list=Invoice.objects.all()
  return render(request, 'royalty_app/invoices.html', {"invoice_list":invoice_list,"periodicity_cat_list":periodicity_cat_list,"contract_partner_list":contract_partner_list,"contract_list":contract_list})

@login_required(login_url='/login')
def static_data(request):
  return render(request, 'royalty_app/static_data.html', {})

@login_required(login_url='/login')
def settings(request):
  return render(request, 'royalty_app/settings.html', {})

@login_required(login_url='/login')
def monthly_accruals(request):
  month_list=Month_table.objects.all()
  file_list=File.objects.filter(file_type="accruals")

  return render(request, 'royalty_app/monthly_accruals.html', {"month_list":month_list,"file_list":file_list})

@login_required(login_url='/login')
def cash_flow_forecast(request):
  month_list=Month_table.objects.all()
  file_list=File.objects.filter(file_type="cash_forecast")
  current_month_nb=datetime.now().month
  return render(request, 'royalty_app/cash_flow_forecast.html', {"current_month_nb":current_month_nb,"month_list":month_list,"file_list":file_list})

@login_required(login_url='/login')
def partner_report(request):
  month_list=Month_table.objects.all()
  file_list=File.objects.filter(file_type="partner_report")
  current_month_nb=datetime.now().month
  return render(request, 'royalty_app/partner_report.html', {"current_month_nb":current_month_nb,"month_list":month_list,"file_list":file_list})



#------------------------------------------------------------------------
#                        API
#------------------------------------------------------------------------
#API Static Data

@login_required
def export(request,file):
  file_list=file.split(',')

  #consolidation_currency=Consolidation_currency.objects.all()[:1].get().currency.currency
  #--- definition of dataframes
  #Country
  list_to_pd=Country.objects.all()
  df_country = pd.DataFrame(list(list_to_pd.values()))

  #Region
  list_to_pd=Region.objects.all()
  df_region = pd.DataFrame(list(list_to_pd.values()))
  if df_region.empty:
    df_region=pd.DataFrame({'No Data': []})


  #Partner
  list_to_pd=Partner.objects.all()
  df_partner = pd.DataFrame(list(list_to_pd.values()))

  #Contract
  list_to_pd=Contract.objects.all()
  df_contract = pd.DataFrame(list(list_to_pd.values()))

  #Contract_partner
  list_to_pd=Contract_partner.objects.all()
  df_contract_partner = pd.DataFrame(list(list_to_pd.values()))

  #Rule
  list_to_pd=Rule.objects.all().values_list('id','contract_id','country_incl_excl','country_list','formulation','period_from','period_to','tranche_type','field_type','rate_value','qty_value')
  df_rule = pd.DataFrame.from_records(list(list_to_pd), columns=['rule_id','contract_id','country_incl_excl','country_list','formulation','period_from','period_to','tranche_type','field_type','rate_value','qty_value'])
  
  #Invoice
  list_to_pd=Invoice.objects.all()
  df_invoice = pd.DataFrame(list(list_to_pd.values()))

  #Payment_structure
  list_to_pd=Payment_structure.objects.all()
  df_payment_structure = pd.DataFrame(list(list_to_pd.values()))

  #Division
  list_to_pd=Division.objects.all()
  df_division = pd.DataFrame(list(list_to_pd.values()))
  if df_division.empty:
    df_division=pd.DataFrame({'No Data': []})

  #Periodicity_cat
  list_to_pd=Periodicity_cat.objects.all()
  df_periodicity_cat = pd.DataFrame(list(list_to_pd.values()))

  #Accounting
  list_to_pd=Accounting.objects.all()
  df_accounting = pd.DataFrame(list(list_to_pd.values()))
  if df_accounting.empty:
    df_accounting=pd.DataFrame({'No Data': []})
  else:
    df_accounting=df_accounting.drop(['id'], axis = 1)

  #Brand
  list_to_pd=Brand.objects.all()
  df_brand = pd.DataFrame(list(list_to_pd.values()))
  if df_brand.empty:
    df_brand=pd.DataFrame({'No Data': []})

  #Tax
  list_to_pd=Tax.objects.all()
  df_tax = pd.DataFrame(list(list_to_pd.values()))
  if df_tax.empty:
    df_tax=pd.DataFrame({'No Data': []})
  else:
    df_tax=df_tax.drop(['id'], axis = 1)
  #Tranche
  
  list_to_pd=Tranche.objects.all()
  df_tranche = pd.DataFrame(list(list_to_pd.values()))
  if df_tranche.empty:
    df_tranche=pd.DataFrame({'No Data': []})
  else:
    df_tranche=df_tranche.drop(['id'], axis = 1)


  #Formulation
  list_to_pd=Formulation.objects.all()
  df_formulation = pd.DataFrame(list(list_to_pd.values()))
  if df_formulation.empty:
    df_formulation=pd.DataFrame({'No Data': []})
  #currency
  list_to_pd=Currency.objects.all()
  df_currency = pd.DataFrame(list(list_to_pd.values()))
  if df_currency.empty:
    df_currency=pd.DataFrame({'No Data': []})
  #Consolidation
  list_to_pd=Consolidation_currency.objects.all()
  df_consolidation_currency = pd.DataFrame(list(list_to_pd.values()))
  if df_consolidation_currency.empty:
    df_consolidation_currency=pd.DataFrame({'No Data': []})
  else:
    df_consolidation_currency=df_consolidation_currency.drop(['id'], axis = 1)

  #payment type
  list_to_pd=Payment_type.objects.all()
  df_payment_type = pd.DataFrame(list(list_to_pd.values()))

  #Periodicity
  list_to_pd=Periodicity.objects.all()
  df_periodicity = pd.DataFrame(list(list_to_pd.values()))
  
  #Payment Type
  list_to_pd=Payment_type.objects.all()
  df_payment_type = pd.DataFrame(list(list_to_pd.values()))
  if df_payment_type.empty:
    df_payment_type=pd.DataFrame({'No Data': []})

  #--- customize dataframe to make them easy to read:
  #Partners
  if df_partner.empty:
    df_partner=pd.DataFrame({'No Data': []})
  else:
    df_partner=pd.merge(df_partner,df_payment_type, how="inner",left_on=['partner_payment_type_id'], right_on=['id'] ) 
    df_partner=df_partner.rename(columns={'id_x':'partner_id','partner_country_id':'partner_country'})
    df_partner=df_partner[['partner_id','partner_name','partner_m3_code','partner_country','partner_bank_account','payment_type']]

  #Contract
  if df_contract.empty:
    df_contract=pd.DataFrame({'No Data': []})
  else:
    df_contract=pd.merge(df_contract,df_periodicity, how="inner",left_on=['payment_periodicity_id'], right_on=['id'] ) 
    df_contract=pd.merge(df_contract,df_brand, how="inner",left_on=['m3_brand_id'], right_on=['id'] ) 
    df_contract=df_contract.rename(columns={'brand_name':'brand','id_x':'contract_id','division_id':'division','division_via_id':'division_via','contract_currency_id':'contract_currency','minimum_guar_remaining_allocation_country_id':'minimum_guar_remaining_allocation_country'})
    df_contract=df_contract[['contract_id','contract_name','transaction_direction','division','division_via','contract_currency','periodicity','payment_terms','brand','mini_gar_status','minimum_guar_amount','minimum_guar_remaining_allocation_country']]

  #Contract-partner
  if df_contract_partner.empty:
    df_contract_partner=pd.DataFrame({'No Data': []})
  else:
    df_contract_partner=pd.merge(df_contract_partner,df_contract, how="inner",left_on=['contract_id'], right_on=['contract_id'] ) 
    df_contract_partner=pd.merge(df_contract_partner,df_partner, how="inner",left_on=['partner_id'], right_on=['partner_id'] ) 
    df_contract_partner=df_contract_partner[['contract_name','partner_name','percentage']]

  #Invoices
  if df_invoice.empty:
    df_invoice=pd.DataFrame({'No Data': []})
  else:
    df_invoice=pd.merge(df_invoice,df_contract, how="inner",left_on=['contract_id'], right_on=['contract_id'] ) 
    df_invoice=pd.merge(df_invoice,df_partner, how="inner",left_on=['partner_id'], right_on=['partner_id'] ) 
    df_invoice=pd.merge(df_invoice,df_periodicity_cat, how="inner",left_on=['periodicity_cat_id'], right_on=['id'] ) 
    df_invoice=df_invoice[['contract_name','partner_name','amount','year','periodicity_cat','comment','paid']]

  #Rule
  if df_rule.empty:
    df_rule=pd.DataFrame({'No Data': []})
  else:
    df_rule=pd.merge(df_rule,df_contract, how="inner",left_on=['contract_id'], right_on=['contract_id'] ) 
    df_rule=df_rule.rename(columns={'id_x':'rule_id'})
    df_rule=df_rule[['rule_id','contract_name','country_incl_excl','country_list','formulation','period_from','period_to','tranche_type','field_type','rate_value','qty_value']]

  #Country_list

  if df_country.empty:
    df_country=pd.DataFrame({'No Data': []})
  else:
    df_country=pd.merge(df_country,df_region, how="inner",left_on=['country_region_id'], right_on=['id'] ) 
    df_country=df_country[['country_id','country','region']]

  with BytesIO() as b:
    # Use the StringIO object as the filehandle.
    writer = pd.ExcelWriter(b, engine='xlsxwriter')
    for table_name in file_list:

      if table_name=="partner":
        df_partner.to_excel(writer, sheet_name='Partners',index=False)

      if table_name=="division":
        df_division.to_excel(writer, sheet_name='Galderma Division',index=False)

      if table_name=="contract":
        df_contract.to_excel(writer, sheet_name='Contracts',index=False)

      if table_name=="contract_partner":
        df_contract_partner.to_excel(writer, sheet_name='Contract_partner',index=False)

      if table_name=="invoice":
        df_invoice.to_excel(writer, sheet_name='Invoices',index=False)

      if table_name=="rule":
        df_rule.to_excel(writer, sheet_name='Rules',index=False)

      if table_name=="tranche":
        df_tranche.to_excel(writer, sheet_name='Tranches',index=False)

      if table_name=="country":
        df_country.to_excel(writer, sheet_name='Countries',index=False)

      if table_name=="region":
        df_region.to_excel(writer, sheet_name='Regions',index=False)

      if table_name=="formulation":
        df_formulation.to_excel(writer, sheet_name='Formulations',index=False)

      if table_name=="brand":
        df_brand.to_excel(writer, sheet_name='Brands',index=False)

      if table_name=="currency":
        df_currency.to_excel(writer, sheet_name='Currencies',index=False)

      if table_name=="consolidation_currency":
        df_consolidation_currency.to_excel(writer, sheet_name='Consolidation currency',index=False)

      if table_name=="accounting":
        df_accounting.to_excel(writer, sheet_name='Accounting rules',index=False)

      if table_name=="tax":
        df_tax.to_excel(writer, sheet_name='Tax Rules',index=False)

      if table_name=="payment_type":
        df_payment_type.to_excel(writer, sheet_name='Payment Type',index=False)


    writer.save()

    # if there is only one file selected, we display a specific name- other wise we just list the files

    filename =f"export static files "

    content_type = 'application/vnd.ms-excel'
    response = HttpResponse(b.getvalue(), content_type=content_type)
    response['Content-Disposition'] = 'attachment; filename="' + filename + '.xlsx"'
    return response

  #API Partner:
@csrf_exempt 
@login_required
def change_row(request,partner_id):

  try:
    partner = Partner.objects.get( id=partner_id)
  except partner.DoesNotExist:
    return JsonResponse({"error": "post not found."}, status=404)

  if request.method == "PUT":
    data = json.loads(request.body)
    partner.partner_m3_code = data["partner_m3_code"]
    partner.partner_name = data["partner_name"]
    partner.ico_3rd = data["ico_3rd"]
    partner.partner_country=Country.objects.get(country_id=data["country_id"])
    partner.partner_bank_account = data["partner_bank_account"]
    partner.partner_payment_type=Payment_type.objects.get(id=data["partner_payment_type_id"])
    partner.save()
    return JsonResponse({
      "result": "all done"
    
    
    }, status=201)

  else:
    return JsonResponse({"error": "GET or PUT request required."}, status=400)

@login_required
def cancel_row_partner(request,partner_id):
  try:
    partner = Partner.objects.get( id=partner_id)
  except partner.DoesNotExist:
    return JsonResponse({"error": "post not found."}, status=404)

  if request.method == "GET":
    return JsonResponse({
      "partner_name": partner.partner_name,
      "country_id": partner.partner_country.country_id,
      "country_name": partner.partner_country.country,
      "ico_3rd": partner.ico_3rd,
      "partner_bank_account": partner.partner_bank_account,
      "partner_payment_type_id": partner.partner_payment_type.id,
      "partner_payment_type":partner.partner_payment_type.payment_type,
      "partner_m3_code":partner.partner_m3_code,
  
      })

  else:
    return JsonResponse({"error": "GET or PUT request required."}, status=400) 

@csrf_exempt 
@login_required
def delete_row_partner(request,partner_id):

  if request.method == "POST":
    try:
      partner=Partner.objects.get(pk=partner_id)
      partner.delete()
      return JsonResponse({"result": "all done"}, status=201)
    except ProtectedError as e:
      message=f"{e}"
      message=message.replace('(', '').replace(')', '')
      return JsonResponse({"error": message}, status=400)
    except:
      return JsonResponse({"error": "something went wrong"}, status=400) 
  else:
    return JsonResponse({"error": "GET or PUT request required."}, status=400)


#API to save new partner
@csrf_exempt 
@login_required
def new_partner(request):
  if request.method == "POST":
    try:
      data = json.loads(request.body)
      partner=Partner(
        partner_m3_code = data["partner_m3_code"],
        partner_name = data["partner_name"],
        ico_3rd = data["ico_3rd"],
        partner_country=Country.objects.get(country_id=data["country_id"]),
        partner_bank_account = data["partner_bank_account"],
        partner_payment_type=Payment_type.objects.get(id=data["partner_payment_type_id"]),
      )
      partner.save()

      return JsonResponse({"partner_id": partner.id}, status=201)
    except: return JsonResponse({"error": "data not loaded"}, status=404)
@csrf_exempt
@login_required
def save_paid_status(request):
  if request.method == "POST":  
    data = json.loads(request.body)
    invoice_id=data["invoice_id"]
    invoice=Invoice.objects.get(id=invoice_id)
    invoice.paid=data["paid"]
    invoice.save()

    return JsonResponse({"message": "all done"}, status=201)
  #----------------------------------------------------------
  #API Contracts:
@csrf_exempt
@login_required 
def change_row_contract(request,contract_id):

  try:
    contract = Contract.objects.get( id=contract_id)
  except contract.DoesNotExist:
    return JsonResponse({"error": "post not found."}, status=404)

  if request.method == "PUT":
    data = json.loads(request.body)

    #division via/Mini Gar Country are not mandatory-
    if data["country_id"] == "" : 
      minimum_guar_remaining_allocation_country= None
    else :
      minimum_guar_remaining_allocation_country=Country.objects.get(country_id=data["country_id"])
    if data["division_via_id"] == "" : 
      division_via= None
    else :
      division_via=Division.objects.get(division_id=data["division_via_id"])
    if data["minimum_guar_amount"] == "" : 
      minimum_guar_amount= None
    else :
      minimum_guar_amount=data["minimum_guar_amount"] 

    contract.contract_name = data["contract_name"]
    contract.transaction_direction = data["transaction_direction"]
    contract.division=Division.objects.get(division_id=data["division_id"])
    contract.division_via=division_via
    contract.payment_periodicity=Periodicity.objects.get(id=data["payment_periodicity_id"])
    contract.payment_terms = data["payment_terms"]
    contract.m3_brand=Brand.objects.get(id=data["brand_id"])
    contract.mini_gar_status = data["mini_gar_status"]
    contract.minimum_guar_amount = minimum_guar_amount
    contract.minimum_guar_remaining_allocation_country=minimum_guar_remaining_allocation_country
    contract.save()
    return JsonResponse({"result": "all done"}, status=201)

  else:
    return JsonResponse({"error": "GET or PUT request required."}, status=400)

#API to save new contract
@csrf_exempt
@login_required 
def new_contract(request):
  if request.method == "POST":
    data = json.loads(request.body)
    #division via/Mini Gar Country are not mandatory-
    if data["country_id"] == "" : 
      minimum_guar_remaining_allocation_country= None
    else :
      minimum_guar_remaining_allocation_country=Country.objects.get(country_id=data["country_id"])
    if data["division_via_id"] == "" : 
      division_via= None
    else :
      division_via=Division.objects.get(division_id=data["division_via_id"])
    if data["minimum_guar_amount"] == "" : 
      minimum_guar_amount= None
    else :
      minimum_guar_amount=data["minimum_guar_amount"] 
    try:  
      contract=Contract(
        contract_name = data["contract_name"],
        transaction_direction = data["transaction_direction"],
        division=Division.objects.get(division_id=data["division_id"]),
        division_via=division_via,
        contract_currency=Currency.objects.get(currency=data["contract_currency_id"]),
        payment_periodicity=Periodicity.objects.get(id=data["periodicity_id"]),
        payment_terms = data["payment_terms"],
        m3_brand=Brand.objects.get(id=data["brand_id"]),
        mini_gar_status = data["mini_gar_status"],
        minimum_guar_amount = minimum_guar_amount,
        minimum_guar_remaining_allocation_country=minimum_guar_remaining_allocation_country,
      )
      contract.save()
      return JsonResponse({"contract_id": contract.id}, status=201)
    except: return JsonResponse({"error": "data not loaded"}, status=404)

@csrf_exempt 
@login_required
def delete_row_contract(request,contract_id):
  if request.method == "POST":
    try:
      contract=Contract.objects.get(pk=contract_id)
      contract.delete()
      return JsonResponse({"result": "all done"}, status=201)
    except ProtectedError as e:
      message=f"{e}"
      message=message.replace('(', '').replace(')', '')
      return JsonResponse({"error": message}, status=400) 

    except:
      return JsonResponse({"error": "somthing went wrong"}, status=400) 
  else:
    return JsonResponse({"error": "GET or PUT request required."}, status=400)
@login_required
def cancel_row_contract(request,contract_id):
  try:
    contract = Contract.objects.get( id=contract_id)
  except contract.DoesNotExist:
    return JsonResponse({"error": "post not found."}, status=404)

  if request.method == "GET":
    # for division_via, mini gar country/amount, the user to not need to submit anything- in order to avoid a None/ or error, we must insert a default value
    #Division via
    if contract.division_via is None:
      division_via_id=""
    else:
      division_via_id=contract.division_via.division_id
    #Mini Gar country
    if contract.minimum_guar_remaining_allocation_country is None:
      country_id=""
      country_name=""
    else:
      country_id=contract.minimum_guar_remaining_allocation_country.country_id
      country_name=contract.minimum_guar_remaining_allocation_country.country
    #Mini Gar  amount
    if contract.minimum_guar_amount is None:
      minimum_guar_amount=""
    else:
      minimum_guar_amount=contract.minimum_guar_amount

    return JsonResponse({
      "contract_name": contract.contract_name,
      "transaction_direction": contract.transaction_direction,
      "division_id": contract.division.division_id,
      "division_via_id": division_via_id,
      "contract_currency": contract.contract_currency.currency,
      "payment_periodicity_name":contract.payment_periodicity.periodicity,
      "payment_periodicity_id":contract.payment_periodicity.id,
      "payment_terms":contract.payment_terms,
      "m3_brand_id":contract.m3_brand.id,
      "m3_brand_name":contract.m3_brand.brand_name,
      "mini_gar_status":contract.mini_gar_status,
      "minimum_guar_amount":minimum_guar_amount,
      "country_id":country_id,
      "country_name":country_name,
      })

  else:
    return JsonResponse({"error": "GET or PUT request required."}, status=400) 

@csrf_exempt 
@login_required
def save_contract_partner(request,contract_id):
  if request.method == "POST":
    contract=Contract.objects.get(id=contract_id)
    Contract_partner_before_modification=Contract_partner.objects.filter(contract=contract)
    Contract_partner.objects.filter(contract=contract).delete()    #delete the existing record for this contract_partner ( we replace then, see code after:)
    data = json.loads(request.body)

    for item in data :
      try:  
        cp=Contract_partner(
          contract = contract,
          partner = Partner.objects.get(id=item[0]),
          percentage=item[1],
        )
        cp.save()
      except Exception as e:
        for  c in Contract_partner_before_modification:
          c.save()
        return JsonResponse({"error": f"data not loaded-   server message: {e}"}, status=404)
    return JsonResponse({"response": "OK"}, status=201)
  else:
    return JsonResponse({"error": "GET or PUT request required."}, status=400)

@csrf_exempt
@login_required
def save_rule(request,contract_id):

  if request.method == "POST":
    contract=Contract.objects.get(id=contract_id)
    rules_before_modification=Rule.objects.filter(contract=contract)
    Rule.objects.filter(contract=contract).delete()    #delete the existing record for this contract_partner ( we replace then, see code after:)
    data = json.loads(request.body)
    print(data)
    for item in data :
      try:  

        if item['Report_currency']=="same_as_contract" :
          report_currency=contract.contract_currency
        if (', '.join(item['country']))=='' :
          country_list='---'
        else:
          country_list=', '.join(item['country'])

        qty_value_currency=Currency.objects.get(currency=item['qty_value_currency'])

        r=Rule(
          contract = contract,
          country_incl_excl=item['country_incl_excl'],
          field_type=item['field_type'],
          period_from=item['period_from'],
          period_to=item['period_to'],
          tranche_type=item['tranche_type'],
          rate_value=item['rate_value'],
          qty_value=item['qty_value'],
          qty_value_currency=qty_value_currency,
          report_currency=report_currency,
          country_list=country_list
        )

        r.save()
        #add formulation
        formulation_list=Formulation.objects.filter(formula_code__in= item['formulation'])
        r.formulation.add(*formulation_list)
        #add country
        country_list=Country.objects.filter(country_id__in= item['country'])
        r.country.add(*country_list)
        #add tranches
        tranche_list=item['tranche_list']
        if tranche_list != [] :
          for tranche_row in tranche_list:
            t=Tranche(
              rule=r,
              from_amount=tranche_row['from_tranche'],
              to_amount=tranche_row['to_tranche'],
              percentage=tranche_row['rate_tranche'],
            )
            t.save()
      except Exception as e:
        for  r in rules_before_modification:
          r.save()
        return JsonResponse({"error": f"data not loaded-   server message: {e}"}, status=404)
    return JsonResponse({"response": "OK"}, status=201)
  else:
    return JsonResponse({"error": "GET or PUT request required."}, status=400)



@csrf_exempt 
@login_required
def save_invoice_breakdown(request,contract_id):
  if request.method == "POST":
    contract=Contract.objects.get(id=contract_id)
    Sales_breakdown_per_contract.objects.filter(contract=contract).delete()    #delete the existing record for this contract_partner ( we replace then, see code after:)
    data = json.loads(request.body)

    for item in data :

      try:  
        s=Sales_breakdown_per_contract(
          contract = contract,
          sales_breakdown_item = Sales_breakdown_item.objects.get(id=item["id"]),
          sales_breakdown_contract_definition=item["sales_breakdown_contract_definition"],
        )
        s.save()
      except Exception as e:
        return JsonResponse({"error": f"data not loaded-   server message: {e}"}, status=404)
    return JsonResponse({"response": "OK"}, status=201)
  else:
    return JsonResponse({"error": "GET or PUT request required."}, status=400)


@csrf_exempt
@login_required
def new_invoice(request):
  if request.method == "POST":
    data = json.loads(request.body)
    print(data)
    try:  
      invoice=Invoice(
        contract = Contract.objects.get(id=data["contract_id"]),
        partner = Partner.objects.get(id=data["partner_id"]),
        amount=data["amount_value"],
        booking_date=data["booking_date"],
        year=data["year_value"],
        periodicity_cat= Periodicity_cat.objects.get(id=data["period_id"]),
        comment = data["comment_value"],
      )
      invoice.save()
      
      return JsonResponse({"invoice_id": invoice.id}, status=201)
    except Exception as e:
      return JsonResponse({"error": f"data not loaded-   server message: {e}"}, status=404)

@csrf_exempt
@login_required
def new_contract_file(request): 
  if request.method == "POST":
    try:  
      contract_file=Contract_file(
        name = request.POST.get("name"),
        contract = Contract.objects.get(id=request.POST.get("contract_id")),
        upload=request.FILES.get("file"),
      )
      contract_file.save()
      return JsonResponse({"cf_id": contract_file.id, "cf_url":contract_file.upload.url}, status=201)
    except Exception as e:
      return JsonResponse({"error": f"data not loaded-   server message: {e}"}, status=404)

@csrf_exempt
@login_required
def delete_contract_file(request,cf_id):
  if request.method == "POST":
    contract_file=Contract_file.objects.get(pk=cf_id)
    contract_file.delete()
    return JsonResponse({"result": "all done"}, status=201)
  else:
    return JsonResponse({"error": "GET or PUT request required."}, status=400)


@csrf_exempt
@login_required
def delete_row_invoice(request,invoice_id):
  if request.method == "POST":
    invoice=Invoice.objects.get(pk=invoice_id)
    invoice.delete()
    return JsonResponse({"result": "all done"}, status=201)
  else:
    return JsonResponse({"error": "GET or PUT request required."}, status=400)


@csrf_exempt
@login_required
def delete_row_file(request,file_id):
  if request.method == "POST":
    try:
      file=File.objects.get(pk=file_id)
      file.delete()
      return JsonResponse({"result": "all done"}, status=201)
    except ProtectedError as e:
      message=f"{e}"
      message=message.replace('(', '').replace(')', '')
      return JsonResponse({"error": message}, status=400) 
    except:
      return JsonResponse({"error": "somthing went wrong"}, status=400)
  else:
    return JsonResponse({"error": "GET or PUT request required."}, status=400)

@csrf_exempt
@login_required
def save_dashboard(request):
  if request.method == "POST":  
    data = json.loads(request.body)
    file_id=data["file_id"]
    invoice=File.objects.get(id=file_id)
    invoice.dashboard=data["dashboard"]
    invoice.save()

    return JsonResponse({"message": "all done"}, status=201)


#Reports
@csrf_exempt
@login_required
def new_report(request):
# Index:
  #   I: book file name in database
  #   II: Start Calculation Roy 
  #       a- definition and import table 
  #       b- calculation of rate per country and formulation
  #         i.:   average rate for contract with tranche
  #       c-Calculation royalty
  #         i   : Roy on sales
  #         ii. : Mini Gar 
  #         iii.: Invoice 
  #         iv. : append of i/ii/iii
  #       d-Calculation conso file
  #       e-Calculation Entry Detail
  #       f-Calculation GLS
  #   III: Save calculation in database

  #   I: book file name in database
  if request.method == "POST":

    #Save File
    try:
      file_type=request.POST.get("file_type")
      if file_type =="accruals":
        acc_year=int(request.POST.get("acc_year"))
        acc_month=int(request.POST.get("acc_month")) 

      else:
        acc_year=datetime.now().year
        acc_month=datetime.now().month
       
    
      file=File(
        name =  request.POST.get("name"),
        acc_year =acc_year,
        acc_month=Month_table.objects.get(month_nb=acc_month),
        file_type=file_type
      )
      file.save()

  #   II: Start Calculation Roy 
      try:
  #   II: Start Calculation Roy 
    #a- definition and import table
        consolidation_currency=Consolidation_currency.objects.all()[:1].get().currency.currency

        #nb month in import file: the goal is to specify the period under analysis
        rows = []
        if file_type =="accruals":
          previous_year_checked= request.POST.get("previous_year_checked")
          
          if previous_year_checked=="true":
            previous_year=acc_year-1
            for i in range(12):
              rows.append([previous_year, i + 1])
          for i in range(acc_month):
            rows.append([acc_year, i + 1])

        else:
          year_from=int(request.POST.get("year_from"))
          year_to=int(request.POST.get("year_to"))
          month_to=int(request.POST.get("month_to"))
          for year_nb in range(year_from,year_to+1):
            if year_nb==year_to :
              for month_nb in range(month_to):
                rows.append([year_nb, month_nb + 1])
            else:
              for month_nb in range(12):
                rows.append([year_nb, month_nb + 1])  

        df_year_month = pd.DataFrame(rows, columns=["year", "month"])    
        df_year_nb_month=df_year_month.groupby(['year']).size().reset_index(name='month_nb')
        print("df_year_nb_month : Done")
   
        #Tranche
        tranche_list=Tranche.objects.all()
        df_tranche = pd.DataFrame(list(tranche_list.values()))

        filehandle = request.FILES.get("file")

        #Rule
        rule_list=Rule.objects.all().values_list('id','contract_id','country_incl_excl','country_list','formulation','period_from','period_to','tranche_type','field_type','rate_value','qty_value','report_currency','qty_value_currency')
        df_rule = pd.DataFrame.from_records(list(rule_list), columns=['rule_id','contract_id','country_incl_excl','country_list','formulation','period_from','period_to','tranche_type','field_type','rate_value','qty_value','report_currency','qty_value_currency'])
        
          #Each rule is composed on a beginning and end date. If the period goes across different years, we must break the row- i.e. 01/01/2019 to 10/10/2020 --> 01/01/2019 to 31/12/2019 // 01/01/2020 to 10/10/2020
        df_rule= df_year_nb_month.merge(df_rule, how="cross" ) #some contracts have a long period (i.e. 01/01/1990 to 01/01/2030), while the period under analysis only concernd a few years- do that reason, we utilise the "df_year_nb_month", which is the period chosen by the user for the analysis 
        filtered_values = np.where((pd.DatetimeIndex(df_rule['period_from']).year <= df_rule['year']) & (pd.DatetimeIndex(df_rule['period_to']).year >= df_rule['year']) ) 
        df_rule=df_rule.loc[filtered_values]
      
        df_rule['month']='1'
        df_rule['day']='1'
        df_rule['period_from']=np.where(
          pd.DatetimeIndex(df_rule['period_from']).year==df_rule['year'],
          pd.to_datetime(df_rule['period_from']), 
          pd.to_datetime(df_rule[['year', 'month','day']], errors = 'coerce')#.astype(str)
        )

        df_rule['month']='12'
        df_rule['day']='31'
        df_rule['period_to']=np.where(
          pd.DatetimeIndex(df_rule['period_to']).year==df_rule['year'],
          pd.to_datetime(df_rule['period_to']), 
          pd.to_datetime(df_rule[['year', 'month','day']], errors = 'coerce')#.astype(str)
        )
     
        df_rule['period_from']=pd.to_datetime(df_rule['period_from'],format='%d.%m.%Y')
        df_rule['period_to']=pd.to_datetime(df_rule['period_to'],format='%d.%m.%Y')

        df_rule=df_rule.drop(['month_nb','month','day'], axis = 1)

        if df_rule.empty: 
          df_rule=pd.DataFrame({
            'year': [0],
            'rule_id': [0],
            'contract_id': [0],
            'country_incl_excl': [''],
            'country_list': ['0'],
            'formulation': ['0'],
            'period_from': ['1900-01-01'],
            'period_to': ['1900-01-01'],
            'tranche_type': [''],
            'field_type': [''],
            'sales_rate': [0],
            'qty_value': [0],
            'report_currency': [''],
            'qty_value_currency': [''],
          })
        print('df_rule')

        #Payment_structure
        payment_structure_list=Payment_structure.objects.all()
        df_payment_structure = pd.DataFrame(list(payment_structure_list.values()))

        #Partner
        partner_list=Partner.objects.all()
        df_partner = pd.DataFrame(list(partner_list.values()))

        #Division
        division_list=Division.objects.all()
        df_division = pd.DataFrame(list(division_list.values()))

        #Month
        month_list=Month_table.objects.all()
        df_month = pd.DataFrame(list(month_list.values()))

        #Periodicity_cat
        periodicity_cat_list=Periodicity_cat.objects.all()
        df_periodicity_cat = pd.DataFrame(list(periodicity_cat_list.values()))
        #df_periodicity_cat=pd.merge(df_periodicity_cat,df_month, how="inner",left_on=['sales_month_id'], right_on=['month_nb'] )

        #Accounting
        accounting_list=Accounting.objects.all()
        df_accounting = pd.DataFrame(list(accounting_list.values()))

        #Country
        country_list=Country.objects.all()
        df_country = pd.DataFrame(list(country_list.values()))
        
        #Brand
        brand_list=Brand.objects.all()
        df_brand = pd.DataFrame(list(brand_list.values()))

        #Tax
        tax_list=Tax.objects.all()
        df_tax = pd.DataFrame(list(tax_list.values()))

        #Sales_breakdown_item
        
        sales_breakdown_item_list=Sales_breakdown_item.objects.all()
        df_sales_breakdown_item = pd.DataFrame(list(sales_breakdown_item_list.values()))
        if df_sales_breakdown_item.empty: 
          df_sales_breakdown_item=pd.DataFrame({
            'id': [0],
            'sales_breakdown_definition': ['NA'],
          })

        #Sales_breakdown_per_contract
        breakdown_per_contract_list=Sales_breakdown_per_contract.objects.all()
        df_breakdown_per_contract = pd.DataFrame(list(breakdown_per_contract_list.values()))
        df_breakdown_per_contract=df_breakdown_per_contract.rename(columns={'contract_id':'contract_id_breakdown'})
        if df_breakdown_per_contract.empty:  
          df_breakdown_per_contract=pd.DataFrame({
            'id': [0],
            'contract_id_breakdown': [0],
            'sales_breakdown_item_id': [0],
            'sales_breakdown_contract_definition': ['NA'],
          })

        df_breakdown_per_contract=pd.merge(df_breakdown_per_contract,df_sales_breakdown_item,how="left",left_on=['sales_breakdown_item_id'], right_on=['id'] )
        df_breakdown_per_contract=df_breakdown_per_contract[['contract_id_breakdown','sales_breakdown_definition','sales_breakdown_contract_definition']]



        #FX
        df_fx = pd.read_excel(filehandle, 'Fx',dtype={'year':int})
        df_fx['import_file_id']=file.id
        df_fx = df_fx[[ 'year','currency','exchange_rate','import_file_id']]
 
        df_fx=pd.merge(df_fx,df_year_nb_month, how="inner",left_on=['year'], right_on=['year'] )
        df_fx=df_fx.drop(['month_nb'], axis = 1)
        if df_fx.empty:
          return JsonResponse({"error": f"No Fx available for the period selected"}, status=201)

        #Contract
        contract_list=Contract.objects.all()
        df_contract = pd.DataFrame(list(contract_list.values()))
        df_contract=df_contract.rename(columns={'id':'contract_id','contract_currency_id':'contract_currency','division_id':'division'})

        #Contract_partner
        contract_partner_list=Contract_partner.objects.all()
        df_contract_partner = pd.DataFrame(list(contract_partner_list.values()))
        if df_contract_partner.empty:  
          df_contract_partner=pd.DataFrame({
            'contract_id': [0],
            'partner_id': [0],
            'percentage': [0],
          })
        #Invoice
        
        invoice_list=Invoice.objects.all()
        df_invoice = pd.DataFrame(list(invoice_list.values()))
          # if the dataframe is empty, we create one --> this step is necessary, as later on we append the table from Invoice + Minigar + Roy on sales
        df_invoice_empty=pd.DataFrame({
            'id': [0],
            'contract_id': [0],
            'partner_id': [0],
            'amount': [0],
            'month': [0],
            'year': [0],
            'periodicity_cat_id': [0],
            'comment': [''],
            'paid': [False],
          })        
        if df_invoice.empty:
          df_invoice=df_invoice_empty
        else:
          df_invoice['month_booking']=pd.DatetimeIndex(df_invoice['booking_date']).month # we filter the invoice booked during the period under analysis
          df_invoice['year_booking']=pd.DatetimeIndex(df_invoice['booking_date']).year
          df_invoice=pd.merge(df_invoice,df_year_month, how="inner",left_on=['year_booking','month_booking'], right_on=['year','month'] )
          df_invoice = df_invoice.rename(columns={'year_x': 'year'})
          df_invoice=df_invoice.drop(['month_booking','year_booking','year_y','month'], axis = 1)

          # if the invoices have been booked at a time not mentionned in the from/to period, the dataframe will be empty- same as mention before, we must fill in the table anyway
          if df_invoice.empty:
            df_invoice=df_invoice_empty

        print("definition of DF expect Sale: Done")

        #Sale
          #same logic as for the FX
        df_sales = pd.read_excel(filehandle, 'Sales',dtype={'SKU':str,'formulation':str,'year':int,'month':int})
        df_sales_empty=pd.DataFrame({
            'year': [0],
            'month': [0],
            'country_id': [''],
            'formulation': [''],
            'volume': [0],
            'sales': [0],
            'sales_currency': [''],
          })
        if df_sales.empty:
          df_sales=df_sales_empty
        else: 
          df_sales=pd.merge(df_sales,df_year_month, how="inner",left_on=['year','month'], right_on=['year','month'] )
          if df_sales.empty:
            df_sales=df_sales_empty
          print("df_sales")
        df_sales['import_file_id']=file.id
          # in the event the user load a data without the SKU and SKU_name ( for accruals and CCF), we should create the below columns
        if 'SKU' not in df_sales.head() :
          df_sales["SKU"]=None
        if 'SKU_name' not in df_sales.head() :
          df_sales["SKU_name"]=None
        df_sales['SKU']=df_sales['SKU'].astype(str)


        df_sales_breakdown=df_sales.copy()
        df_sales=df_sales[['year','month','country_id','formulation','SKU','SKU_name','sales_currency','import_file_id','volume','sales']]
        print("definition of df_sales: Done")

        #--------Calculate sales break_down so that the user can see the breakdown per contract----------
        #first, break the import
        if file.file_type=="partner_report" :
          df_sales_breakdown=pd.melt(
            df_sales_breakdown,
            id_vars=['year','month','country_id','formulation','SKU','SKU_name','sales_currency','import_file_id','volume'],
            var_name="sales_breakdown_definition",
            value_name="sales_in_market_curr",
          )

          #df_sales_breakdown[['sales_in_market_curr']]=df_sales_breakdown[['sales_in_market_curr']].astype(float)
          df_sales_breakdown[['sales_in_market_curr']] = df_sales_breakdown[['sales_in_market_curr']].fillna(value=0)
          #remove column with no sales ( only apply for the row that are not Sales)

          df_sales_breakdown["is_null"]=(df_sales_breakdown["sales_in_market_curr"]==0) & (df_sales_breakdown["sales_breakdown_definition"]!="sales")
          df_sales_breakdown=df_sales_breakdown[df_sales_breakdown.is_null == False]
          df_sales_breakdown=df_sales_breakdown.drop(['is_null'], axis = 1)

          #remove duplicate for volume"
          df_sales_breakdown["volume"]=np.where(
            df_sales_breakdown["sales_breakdown_definition"]=="sales",
            df_sales_breakdown["volume"],
            0,
          )
  
          #import contract + contract curr + FX ( for conversion to contract curr): 
          print("df_sales_breakdown 0")

          df_sales_breakdown=pd.merge(df_rule,df_sales_breakdown, how="inner",left_on=['formulation'], right_on=['formulation'] )
          if not df_sales_breakdown.empty :
            df_sales_breakdown['country_validation']=(
                                        ((df_sales_breakdown.apply(lambda x: x.country_id in x.country_list, axis=1))& (df_sales_breakdown['country_incl_excl'] == "INCLUDE") ) | 
                                        ((df_sales_breakdown.apply(lambda x: x.country_id not in x.country_list, axis=1))& (df_sales_breakdown['country_incl_excl'] == "EXCLUDE") )
                                      )
            print("df_sales_breakdown 1")

            df_sales_breakdown['day']="1"

            df_sales_breakdown['date'] = pd.to_datetime(df_sales_breakdown[['year', 'month','day']], errors = 'coerce')
            df_sales_breakdown['date_validation']=((df_sales_breakdown['date']>=df_sales_breakdown['period_from']) & (df_sales_breakdown['date']<=df_sales_breakdown['period_to']))
            df_sales_breakdown=df_sales_breakdown[df_sales_breakdown.date_validation ==True]
            df_sales_breakdown=df_sales_breakdown[df_sales_breakdown.country_validation ==True]

            print("df_sales_breakdown 2")

            # df_on_sales and contract
            df_sales_breakdown=pd.merge(df_sales_breakdown,df_contract, how="inner",left_on=['contract_id'], right_on=['contract_id'] )
            print("df_sales_breakdown 3")
            #df_on_sales and fx 
            df_sales_breakdown=pd.merge(df_sales_breakdown,df_fx, how="inner",left_on=['year','sales_currency'], right_on=['year','currency'] )
            df_sales_breakdown = df_sales_breakdown.rename(columns={'exchange_rate': 'exchange_rate_sales_curr'})
            df_sales_breakdown=pd.merge(df_sales_breakdown,df_fx, how="inner",left_on=['year','contract_currency'], right_on=['year','currency'] )
            df_sales_breakdown = df_sales_breakdown.rename(columns={'exchange_rate': 'exchange_rate_contract_curr'})
            print("df_sales_breakdown 4")
            df_sales_breakdown["sales_in_contract_curr"]=df_sales_breakdown["sales_in_market_curr"]*df_sales_breakdown["exchange_rate_sales_curr"]/df_sales_breakdown["exchange_rate_contract_curr"]
            df_sales_breakdown=df_sales_breakdown[['contract_id','contract_name','year','month','country_id','formulation','SKU','SKU_name','sales_currency','import_file_id','volume','sales_in_market_curr','sales_in_contract_curr','sales_breakdown_definition','contract_currency']]

            #link to breakdown def:


            df_sales_breakdown=pd.merge(df_sales_breakdown,df_breakdown_per_contract, how="left",left_on=['contract_id','sales_breakdown_definition'], right_on=['contract_id_breakdown','sales_breakdown_definition'] )
            df_sales_breakdown=df_sales_breakdown[['import_file_id','contract_name','year','month','country_id','formulation','SKU','SKU_name','sales_currency','volume','sales_breakdown_definition','sales_breakdown_contract_definition','contract_currency','sales_in_market_curr','sales_in_contract_curr']]       
          else:
            return JsonResponse({"error": f"No sales data to display- please make sure you "}, status=201)
       
    
        #---------------------------------------
        
    #b- calculation of rate per country and formulation
      #         i.  : average rate for contract with tranche  

        if not df_tranche.empty : 
          t1= pd.merge(df_rule,df_contract, how="inner",left_on=['contract_id'], right_on=['contract_id'] )
          #t1 and Sale
          print('t1')
          print(t1)



          t2=pd.merge(t1,df_sales, how="inner",left_on=['formulation','year'], right_on=['formulation' ,'year'])
          print('t2 beginning')
          print(t2)
          if not t2.empty:
            t2['country_validation']=(
                                      ((t2.apply(lambda x: x.country_id in x.country_list, axis=1))& (t2['country_incl_excl'] == "INCLUDE") ) | 
                                      ((t2.apply(lambda x: x.country_id not in x.country_list, axis=1))& (t2['country_incl_excl'] == "EXCLUDE") )
                                    )
            t2['day']="1"
            t2['date'] = pd.to_datetime(t2[['year', 'month','day']], errors = 'coerce')
            t2['date_validation']=((t2['date']>=t2['period_from']) & (t2['date']<=t2['period_to']))

            t2=t2[t2.date_validation ==True]
            t2=t2[t2.country_validation ==True]
            
            t2=t2[['rule_id','contract_currency','sales','sales_currency','report_currency','year']]
            print("T2")
            print(t2)
            #t2 and fx - get sales currency
            t3=pd.merge(t2,df_fx, how="inner",left_on=['year','sales_currency'], right_on=['year','currency'] )
            t3 = t3.rename(columns={'exchange_rate': 'exchange_rate_from'})
            t3=pd.merge(t3,df_fx, how="inner",left_on=['year','report_currency'], right_on=['year','currency'] )
            t3 = t3.rename(columns={'exchange_rate': 'exchange_rate_to'})
            # calculate sales amount in report currency
            t3['sales_in_report_curr']=t3['sales']*t3['exchange_rate_from']/t3['exchange_rate_to']
            t3=t3.fillna("")
            print("T3")
            print(t3)
            #t4=t3[['rule_id','sales_in_report_curr']].groupby(['rule_id']).sum()
            t4=t3.groupby(['rule_id','year'], as_index=False).agg({"sales_in_report_curr": "sum"})
            #t5 - calculate amount sales and roy
            print("T4")
            print(t4)

            t5=pd.merge(df_tranche,t4, how="left",left_on=['rule_id'], right_on=['rule_id'] )
            t5['amount']=  np.where(
              t5['sales_in_report_curr']>=t5['from_amount'] , 
                np.where(t5['sales_in_report_curr']<t5['to_amount'],
                  t5['sales_in_report_curr']-t5['from_amount'],
                  np.where(t5['to_amount']==0 ,
                    t5['sales_in_report_curr']-t5['from_amount'],
                    t5['to_amount']-t5['from_amount']
                  )
                )
              , 0
            )
            t5['mini_rate']=np.where(t5['from_amount']==0,t5['percentage'],0)
            t5['roy']=t5['amount']*t5['percentage']/100
            t5=t5[['rule_id','amount','roy','mini_rate','year']]
            #t6 - average rate
            t5=t5.fillna("")
            print("T5")
            print(t5)
            t6=t5.groupby(['rule_id','year'], as_index=False).agg({"roy": "sum","amount":"sum","mini_rate":"max"})
            t6['average_rate']=np.where(t6['amount']==0,
                                t6['mini_rate'],
                                t6['roy']/t6['amount']*100
                                ) 
            print('t6')
            print(t6)
            print('df_rule')
            print(df_rule)
            #-----------------link tranche average rate to general Rule -----------------
            df_rule_calc=pd.merge(df_rule,t6, how="left",left_on=['rule_id','year'], right_on=['rule_id','year'] )
            df_rule_calc['sales_rate']=np.where(pd.notna(df_rule_calc['average_rate']),df_rule_calc['average_rate'],df_rule_calc['rate_value'])
            df_rule_calc=df_rule_calc.drop(['average_rate','amount','roy','rate_value','mini_rate'], axis = 1)
            print("definition of rule done")
          else:
            df_rule_calc=df_rule.copy()
            df_rule_calc=df_rule_calc.rename(columns={'rate_value': 'sales_rate'})             
        else:
          df_rule_calc=df_rule.copy()
          df_rule_calc=df_rule_calc.rename(columns={'rate_value': 'sales_rate'}) 
        print("definition of rule done")

    #       c-Calculation royalty
      #         i   : Roy on sales
        #Here we calculate the roy based on the sales reported in the Excel file. i.e. : if roy is 150 USD, and %rate is 10 , then roy=15
        #If there are no sales on the period, of there are no match between the contract and the sales report, the dataframe ( result) would be empty
        #we would like to avoid that situation, as the roy calculated on sales are used to calculate the mini gar

        df_on_sales=pd.merge(df_rule_calc,df_sales, how="inner",left_on=['formulation','year'], right_on=['formulation','year'] )
        print(df_rule_calc)
        print(df_on_sales)
        
        if not df_on_sales.empty:
          #df_on_sales=df_on_sales.drop(['year'], axis = 1)  
          df_on_sales['country_validation']=(
                                      ((df_on_sales.apply(lambda x: x.country_id in x.country_list, axis=1))& (df_on_sales['country_incl_excl'] == "INCLUDE") ) | 
                                      ((df_on_sales.apply(lambda x: x.country_id not in x.country_list, axis=1))& (df_on_sales['country_incl_excl'] == "EXCLUDE") )
                                    )
          print("def_on_sales 1")
          df_on_sales['day']="1"
          df_on_sales['date'] = pd.to_datetime(df_on_sales[['year', 'month','day']], errors = 'coerce')
          df_on_sales['date_validation']=((df_on_sales['date']>=df_on_sales['period_from']) & (df_on_sales['date']<=df_on_sales['period_to']))
          df_on_sales=df_on_sales[df_on_sales.date_validation ==True]
          df_on_sales=df_on_sales[df_on_sales.country_validation ==True]
          print("def_on_sales 2")
          # df_on_sales and contract
          df_on_sales=pd.merge(df_on_sales,df_contract, how="inner",left_on=['contract_id'], right_on=['contract_id'] )
          #df_on_sales and fx 
          df_on_sales=pd.merge(df_on_sales,df_fx, how="inner",left_on=['year','sales_currency'], right_on=['year','currency'] )
          df_on_sales = df_on_sales.rename(columns={'exchange_rate': 'exchange_rate_sales_curr'})
          df_on_sales=pd.merge(df_on_sales,df_fx, how="inner",left_on=['year','contract_currency'], right_on=['year','currency'] )
          df_on_sales = df_on_sales.rename(columns={'exchange_rate': 'exchange_rate_contract_curr'})
          df_on_sales=pd.merge(df_on_sales,df_fx, how="inner",left_on=['year','report_currency'], right_on=['year','currency'] )
          df_on_sales = df_on_sales.rename(columns={'exchange_rate': 'exchange_rate_report'})
          df_on_sales=pd.merge(df_on_sales,df_fx, how="inner",left_on=['year','qty_value_currency'], right_on=['year','currency'] )
          df_on_sales = df_on_sales.rename(columns={'exchange_rate': 'exchange_rate_qty_value_curr'})
          print("def_on_sales 3")
          df_on_sales = df_on_sales.rename(columns={'country_id': 'market_id'})
          df_on_sales = df_on_sales.rename(columns={'sales_currency': 'market_curr'})
          df_on_sales = df_on_sales.rename(columns={'sales': 'sales_in_market_curr'})

          # calculate sales amount in contract currency
          df_on_sales['sales_in_contract_curr']=df_on_sales['sales_in_market_curr']*df_on_sales['exchange_rate_sales_curr']/df_on_sales['exchange_rate_contract_curr']
        
          df_on_sales['qty_value_contract_curr']=df_on_sales['qty_value']*df_on_sales['exchange_rate_qty_value_curr']/df_on_sales['exchange_rate_contract_curr']
          print("def_on_sales 4")
          df_on_sales['amount_contract_curr']=np.where(
            df_on_sales['field_type']=='RATE',
            df_on_sales['sales_rate']*df_on_sales['sales_in_contract_curr']/100,
            df_on_sales['qty_value_contract_curr']*df_on_sales['volume']
          )


          df_on_sales=df_on_sales[['contract_id','year','month','SKU','SKU_name','amount_contract_curr','payment_periodicity_id','market_id','sales_in_market_curr','sales_in_contract_curr','volume','market_curr','field_type','sales_rate','qty_value','report_currency','qty_value_currency']]
          df_on_sales=df_on_sales.fillna("")

          print("def_on_sales 5")# // 
          df_on_sales=df_on_sales.groupby(['contract_id','year','month','SKU','SKU_name','payment_periodicity_id','market_id','market_curr','field_type','sales_rate','qty_value','report_currency','qty_value_currency'], as_index=False).agg({"amount_contract_curr": "sum","sales_in_market_curr": "sum","sales_in_contract_curr": "sum","volume":"sum"})

          df_on_sales['entry_type']='Royalties'
          print("definition of Sales done")
        
        else:
          df_on_sales=pd.DataFrame({
            'contract_id': [0],
            'year': [0],
            'month': [0],
            'SKU': [''],
            'SKU_name': [''],
            'payment_periodicity_id': [0],
            'market_id': [''],
            'market_curr': [''],
            'field_type': [''],
            'sales_rate': [0],
            'qty_value': [0],
            'report_currency': [''],
            'qty_value_currency': [0],
            'amount_contract_curr': [0],
            'sales_in_market_curr': [0],
            'sales_in_contract_curr': [0],
            'volume': [0],
          })

      #         ii. : Mini Gar 

        print("Mini Gar2")

        #get contract with mini gar
        df_mini_gar=df_contract.copy()
        df_mini_gar['ismini']=(df_mini_gar['mini_gar_status']=='YES')
        df_mini_gar=df_mini_gar[df_mini_gar.ismini ==True]
        print("Mini Gar3")

        #df_year_nb_month and df_mini_gar
        df_mini_gar=df_mini_gar.merge(df_year_nb_month,how='cross')

        print("Mini Gar4")

        #df_on_sales with group on country_id
        df_on_sales_group=df_on_sales.groupby(['contract_id','year'], as_index=False).sum()
        df_on_sales_group['year']=df_on_sales_group['year'].astype(int)

        #  df_mini_gar and sales
        df_mini_gar= pd.merge(df_mini_gar,df_on_sales_group, how="left",left_on=['contract_id','year'], right_on=['contract_id','year'] )
        #  calculate remaining gar
        print("Mini Gar5")

        df_mini_gar['amount_contract_curr']= np.where( pd.notna(df_mini_gar['amount_contract_curr']),
                                        np.where(df_mini_gar['minimum_guar_amount']/12*df_mini_gar['month_nb']>df_mini_gar['amount_contract_curr'],
                                          df_mini_gar['minimum_guar_amount']/12*df_mini_gar['month_nb']-df_mini_gar['amount_contract_curr'],
                                          0
                                        ),
                                      df_mini_gar['minimum_guar_amount']/12*df_mini_gar['month_nb']
                                      )
        df_mini_gar["month"]=12

        df_mini_gar= df_mini_gar.rename(columns={'minimum_guar_remaining_allocation_country_id':'market_id'})
        print("Mini Gar6")

        df_mini_gar["market_curr"]=None
        df_mini_gar["sales_in_market_curr"]=None
        df_mini_gar["sales_in_contract_curr"]=None
        df_mini_gar["SKU"]=None
        df_mini_gar["SKU_name"]=None
        df_mini_gar["volume"]=None
        df_mini_gar["report_currency"]=None
        df_mini_gar["field_type"]=None
        df_mini_gar["sales_rate"]=None
        df_mini_gar["qty_value"]=None
        df_mini_gar["qty_value_currency"]=None

        df_mini_gar = df_mini_gar.rename(columns={'payment_periodicity_id_x':'payment_periodicity_id'})
        df_mini_gar=df_mini_gar[['contract_id','year','month','SKU','SKU_name','amount_contract_curr','payment_periodicity_id','market_id','sales_in_market_curr','sales_in_contract_curr','volume','market_curr','field_type','sales_rate','qty_value','report_currency','qty_value_currency']]
        df_mini_gar=df_mini_gar.fillna("")
        df_mini_gar=df_mini_gar.groupby(['contract_id','year','month','SKU','SKU_name','payment_periodicity_id','market_id','market_curr','field_type','sales_rate','qty_value','report_currency','qty_value_currency'], as_index=False).agg({"amount_contract_curr": "sum","sales_in_market_curr": "sum","sales_in_contract_curr":"sum"})
        df_mini_gar['entry_type']='Royalties- mini gar'
        print("Mini Gar7")



      #         iii. : append mini gar and roy on sales
        df_mini_gar=df_mini_gar.fillna("")
        df_on_sales=df_on_sales.fillna("")

        
        df_append_mini_roy=df_mini_gar.append(df_on_sales)

        print("df_append_mini_roy1")
        
        #merge with payment structure 


        df_payment_structure=df_payment_structure.rename(columns={'sales_month_id': 'sales_month'})#.astype(str)
        df_payment_terms=pd.merge(df_periodicity_cat,df_payment_structure, how="inner",left_on=['id'], right_on=['periodicity_cat_id'] )
        df_append_mini_roy=pd.merge(df_append_mini_roy,df_payment_terms, how="inner",left_on=['payment_periodicity_id','month'], right_on=['periodicity_id','sales_month'] )  
  
        print("df_append_mini_roy2")    
        df_append_mini_roy=df_append_mini_roy[['contract_id','year','month','SKU','SKU_name','amount_contract_curr','market_id','sales_in_market_curr','sales_in_contract_curr','volume','market_curr','field_type','sales_rate','qty_value','report_currency','qty_value_currency','periodicity_cat_id','entry_type']]
        print("df_append_mini_roy3")
        #merge with contract_partner and calculate amount per partner
        df_append_mini_roy=pd.merge(df_append_mini_roy,df_contract_partner, how="left",left_on=['contract_id'], right_on=['contract_id'] )
        df_append_mini_roy['percentage']=df_append_mini_roy['percentage'].fillna(100) #If the user did not insert a partner, then we should populate those fields
        df_append_mini_roy['partner_id']=df_append_mini_roy['partner_id'].fillna(0)#If the user did not insert a partner, then we should populate those fields
  
        df_append_mini_roy["amount_contract_curr"]=df_append_mini_roy["amount_contract_curr"]*df_append_mini_roy["percentage"]/100

        df_append_mini_roy= df_append_mini_roy.rename(columns={'percentage':'beneficiary_percentage'})
        df_append_mini_roy=df_append_mini_roy[['contract_id','year','month','SKU','SKU_name','amount_contract_curr','market_id','sales_in_market_curr','sales_in_contract_curr','volume','market_curr','field_type','sales_rate','qty_value','report_currency','qty_value_currency','periodicity_cat_id','entry_type','partner_id','beneficiary_percentage']]

        #df_append_mini_roy=df_append_mini_roy.groupby(['contract_id','year','periodicity_cat_id','entry_type','partner_id'], as_index=False).sum()
        df_append_mini_roy['invoice_detail']=""
        df_append_mini_roy['invoice_paid']=""



        print("df_append_mini_roy4")


      #         iv.: Invoice  

        df_invoice=pd.merge(df_year_nb_month,df_invoice, how="inner",left_on=['year'], right_on=['year'] )
        df_invoice['entry_type']='Invoice'
        df_invoice['month']=None
        df_invoice['SKU']=None
        df_invoice['SKU_name']=None
        df_invoice['market_id']=None
        df_invoice['market_curr']=None
        df_invoice['field_type']=None
        df_invoice['sales_rate']=None
        df_invoice['sales_in_market_curr']=None
        df_invoice['sales_in_contract_curr']=None
        df_invoice['volume']=None
        df_invoice['qty_value']=None
        df_invoice['report_currency']=None
        df_invoice['qty_value_currency']=None
        df_invoice['beneficiary_percentage']=None
        df_invoice=df_invoice.rename(columns={'comment': 'invoice_detail','amount':'amount_contract_curr','paid':'invoice_paid'})
        df_invoice=df_invoice[['contract_id','year','month','SKU','SKU_name','amount_contract_curr','market_id','sales_in_market_curr','sales_in_contract_curr','volume','market_curr','field_type','sales_rate','qty_value','report_currency','qty_value_currency','periodicity_cat_id','entry_type','partner_id','beneficiary_percentage','invoice_detail','invoice_paid']]
        print("definition of df_append_mini_roy: Done")
        print(df_invoice)

        #--------------------------------------------

        print("df_invoice: Done")

      #         iv.: Detail : 
        df_append_mini_roy=df_append_mini_roy.fillna("")
        df_invoice=df_invoice.fillna("")

        df_detail=df_append_mini_roy.append(df_invoice)
        
        print("df_detail 0")
        # get last month of the period (i.e. for Q1, it's march)
        df_detail=pd.merge(df_detail,df_periodicity_cat, how="inner",left_on=['periodicity_cat_id'], right_on=['id'] )
        df_detail["day"]="1"
        df_detail = df_detail.rename(columns={"month":"month_of_sales","period_month_end_id":"period_month_end"})
        df_detail["month"]=df_detail["period_month_end"].astype(str)
        
        print("df_detail 01")

        df_detail["date"]= pd.to_datetime(df_detail[['year', 'month','day']], errors = 'coerce')
        df_detail["day_end_period"]= pd.to_datetime(df_detail['date'], format="%Y%m") + MonthEnd(1)
        df_detail=df_detail[['contract_id','year','SKU','SKU_name','month_of_sales','amount_contract_curr','periodicity_cat','market_id','sales_in_market_curr','sales_in_contract_curr','volume','market_curr','field_type','sales_rate','qty_value','report_currency','qty_value_currency','entry_type','partner_id','beneficiary_percentage','invoice_detail','day_end_period','invoice_paid']]
 
        print("df_detail 1")

        # get contract detail, get the payment terms and calculate the payment date 
        df_detail=pd.merge(df_detail,df_contract, how="inner",left_on=['contract_id'], right_on=['contract_id'] )
        df_detail["payment_date"]= df_detail["day_end_period"]+  pd.to_timedelta(df_detail['payment_terms'], unit='d')
        df_detail["payment_date"]= pd.to_datetime(df_detail['payment_date'],format='%d.%m.%Y') #needed, otherwise cannot load in system
        
        print("df_detail 2")

        
        # convert in consolidation curr

        df_detail=pd.merge(df_detail,df_fx, how="inner",left_on=['year','contract_currency'], right_on=['year','currency'] )
        df_detail = df_detail.rename(columns={'exchange_rate': 'exchange_rate_from'})
        df_detail['consolidation_currency']=consolidation_currency
        
        df_detail=pd.merge(df_detail,df_fx, how="inner",left_on=['year','consolidation_currency'], right_on=['year','currency'] )
        df_detail = df_detail.rename(columns={'exchange_rate': 'exchange_rate_to'})
        df_detail['amount_consolidation_curr']=df_detail['amount_contract_curr']*df_detail['exchange_rate_from']/df_detail['exchange_rate_to']
        
        print("df_detail 3")

        #get partner detail and brand
        df_detail=pd.merge(df_detail,df_partner, how="left",left_on=['partner_id'], right_on=['id'] )
        df_detail=pd.merge(df_detail,df_brand, how="inner",left_on=['m3_brand_id'], right_on=['id'] )
        #get division country
        df_detail=pd.merge(df_detail,df_division, how="inner",left_on=['division'], right_on=['division_id'] )
        # we insert the curr of the qty
        df_detail["qty_value"]=np.where(
          df_detail["qty_value"]==0,
          "",
          df_detail["qty_value"].astype(str)+df_detail["qty_value_currency"] 
        )
        df_detail=df_detail.drop(["qty_value_currency"], axis = 1)

        print("df_detail 4")
        

        #filter
        df_detail=df_detail[['division','division_country_id','division_via_id','field_type','year','month_of_sales','SKU','SKU_name','market_id','sales_in_market_curr','sales_in_contract_curr','volume','market_curr','sales_rate','qty_value','beneficiary_percentage','contract_currency','transaction_direction','amount_contract_curr','consolidation_currency','amount_consolidation_curr','contract_id','contract_name','partner_id','ico_3rd','partner_name','partner_country_id','brand_name','m3_brand_code','periodicity_cat','entry_type','invoice_paid','invoice_detail','payment_date']]
        df_detail = df_detail.rename(columns={'division_via_id': 'division_via',"periodicity_cat":"period","year":"year_of_sales"})

        df_detail["payment_date"]=df_detail["payment_date"].astype(str)
        df_detail["invoice_paid"]=df_detail["invoice_paid"].astype(str)


        print("definition of Detail: Done")

        #Tax impact--------------------- 
        if file.file_type=="cash_forecast": 
          df_wht=  df_detail.copy()
          df_wht['entry_type']=(df_wht['entry_type']=="Invoice")
          df_wht=df_wht[df_wht.entry_type ==False]
          df_wht=df_wht.fillna("")
          df_wht=df_wht.groupby(['division','division_country_id','partner_country_id','ico_3rd','partner_name','contract_currency','transaction_direction'], as_index=False).agg({"amount_contract_curr": "sum"})    

          
          df_wht["country_from"]=np.where(
                                  df_wht["transaction_direction"]=="PAY",
                                  np.where(
                                    df_wht["amount_contract_curr"]>0,
                                    df_wht["division_country_id"],
                                    df_wht["partner_country_id"],
                                  ),
                                  np.where(
                                    df_wht["amount_contract_curr"]>0,
                                    df_wht["partner_country_id"],
                                    df_wht["division_country_id"] ,
                                  )
                                )
          df_wht["country_to"]=np.where(
                                df_wht["country_from"]==df_wht["division_country_id"],
                                df_wht["partner_country_id"],
                                df_wht["division_country_id"],
                              )
          df_wht["from_payor"]=np.where(
                                  df_wht["transaction_direction"]=="PAY",
                                  np.where(
                                    df_wht["amount_contract_curr"]>0,
                                    "ICO-" + df_wht["division"] + " (" + df_wht["division_country_id"] + ")",
                                    np.where(
                                      df_wht["ico_3rd"]=="ICO",
                                      "ICO-" + df_wht["partner_name"] + "(" + df_wht["partner_country_id"]+ ")",
                                      "3rd " + "(" + df_wht["partner_country_id"]+ ")"
                                    )  
                                  ),
                                  np.where(
                                    df_wht["amount_contract_curr"]>0,
                                    np.where(
                                      df_wht["ico_3rd"]=="ICO",
                                      "ICO-" + df_wht["partner_name"] + "(" + df_wht["partner_country_id"]+ ")",
                                      "3rd " + "(" + df_wht["partner_country_id"]+ ")"
                                    ) ,
                                    "ICO-" + df_wht["division"] + " (" + df_wht["division_country_id"] + ")"
                                  )
                                )
          df_wht["to_payee"]=np.where(
                                    df_wht["from_payor"]=="ICO-" + df_wht["division"] + " (" + df_wht["division_country_id"] + ")",
                                    np.where(
                                      df_wht["ico_3rd"]=="ICO",
                                      "ICO-" + df_wht["partner_name"] + "(" + df_wht["partner_country_id"]+ ")",
                                      "3rd " + "(" + df_wht["partner_country_id"]+ ")"
                                    ) ,
                                    "ICO-" + df_wht["division"] + " (" + df_wht["division_country_id"] + ")"
                              )
          df_wht['amount_contract_curr']=abs(df_wht['amount_contract_curr'])

          df_wht=df_wht.fillna("")
          df_wht=df_wht.groupby(['country_from','country_to','from_payor','to_payee','contract_currency'], as_index=False).agg({"amount_contract_curr": "sum"})

          df_wht=pd.merge(df_wht,df_tax, how="left",left_on=['country_from','country_to'], right_on=['country_from_id','country_to_id'] )
          df_wht["wht_rate"]=df_wht["wht_rate"].astype(str)
          df_wht["wht_rate"]=np.where(df_wht["country_from"]==df_wht["country_to"],
                                      "0.00%",
                                      np.where(
                                        df_wht["wht_rate"]=="nan",
                                        "Not defined",
                                        df_wht["wht_rate"]+"%"
                                      )
          )

          df_wht=df_wht[['from_payor','to_payee','contract_currency','amount_contract_curr','wht_rate']]
          print("WHT Done")
          #         iv.:  summary cash flow--------------------- 
          # if REC, them - + if invoice -
          df_cash_flow= df_detail.copy()
          df_cash_flow=df_cash_flow.fillna("")
          df_cash_flow=df_cash_flow.groupby(['division','contract_currency','payment_date','entry_type','invoice_paid','transaction_direction'], as_index=False).agg({"amount_contract_curr": "sum"})

        if file.file_type=="accruals":
        #          v.:  Conso for accruals--------------------- 
          df_conso= df_detail.copy()
          df_conso['entry_type']=(df_conso['entry_type']=="Invoice")
          df_conso=df_conso[df_conso.entry_type ==False]

          df_conso["amount_consolidation_curr"]=np.where(df_conso["transaction_direction"]=="REC",-df_conso["amount_consolidation_curr"],df_conso["amount_consolidation_curr"])

          # import country name for market
          df_conso=pd.merge(df_conso,df_country, how="left",left_on=['market_id'], right_on=['country_id'] )

          #only keep columns
          df_conso=df_conso[['year_of_sales','division','brand_name','country','consolidation_currency','amount_consolidation_curr']]

          #sum and group
          df_conso=df_conso.fillna("")
          df_conso=df_conso.groupby(['year_of_sales','division','brand_name','country','consolidation_currency'], as_index=False).sum()     
          print("df_conso")
        #          v.:  GLS for accruals--------------------- 
          df_gls= df_detail.copy()
          df_gls["accruals_contract_curr"]=np.where(df_gls["entry_type"]=="Invoice",-df_gls["amount_contract_curr"],df_gls["amount_contract_curr"])
          df_gls=df_gls[['division','m3_brand_code','brand_name','transaction_direction','contract_currency','accruals_contract_curr']]
          df_gls=df_gls.fillna("")
          df_gls=df_gls.groupby(['division','m3_brand_code','brand_name','transaction_direction','contract_currency'], as_index=False).agg({"accruals_contract_curr": "sum"})
          df_gls=pd.merge(df_gls,df_accounting, how="inner",left_on=['transaction_direction'], right_on=['transaction_direction'] )
          df_gls["dim3"]=np.where(df_gls["pl_bs"]=="PL",df_gls["m3_brand_code"],"")
          df_gls["d_c_if_amount_negativ"]=np.where(df_gls["d_c_if_amount_positiv"]=="C","D","C")
          df_gls["d_c"]=np.where(df_gls["accruals_contract_curr"]>0,df_gls["d_c_if_amount_positiv"],df_gls["d_c_if_amount_negativ"])
          df_gls["accruals_contract_curr"]=abs(df_gls["accruals_contract_curr"])

          df_gls=df_gls.round({'accruals_contract_curr': 0})
          df_gls["text_voucherline"]= 'ACCR. '+ df_gls["brand_name"]
          #Get Date
          df_gls["year"]=file.acc_year
          df_gls["month"]=file.acc_month.month_nb
          df_gls["day"]="1" 
          df_gls["date"]= pd.to_datetime(df_gls[['year', 'month','day']], errors = 'coerce')
          df_gls["accountingdate"]= pd.to_datetime(df_gls['date'], format="%Y%m") + MonthEnd(1)
          df_gls["reverseDate"]= df_gls["accountingdate"]+ timedelta(days=1)
          df_gls["accountingdate"]= df_gls["accountingdate"].dt.strftime('%d.%m.%Y')
          df_gls["reverseDate"]= df_gls["reverseDate"].dt.strftime('%d.%m.%Y')
          

          df_gls["sheet_name"]= "Accounting_" +df_gls["division"]+"_"+df_gls["contract_currency"]
          df_gls=df_gls.sort_values(['sheet_name','pl_bs','brand_name'], ascending=[1,0,1])
          df_gls=df_gls[['sheet_name','division','contract_currency','accountingdate','reverseDate','dim1','dim2','dim3','dim4','accruals_contract_curr','d_c','text_voucherline']]
          print("df_gls")

        #---------------Save in database----------------

        conn = sqlite3.connect('royalty/db.sqlite3')
        

        df_sales.to_sql('royalty_app_sale', con=conn,index=False,if_exists="append")
    
        print("df_sales loaded succesfully")
        df_fx.to_sql('royalty_app_fx', con=conn,index=False,if_exists="append")
        print("df_fx loaded succesfully")
        df_rule_calc['import_file_id']=file.id
        print(df_rule_calc)
        #we import the contract name
        df_rule_calc=pd.merge(df_rule_calc,df_contract, how="left",left_on=['contract_id'], right_on=['contract_id'] )
        
        # we insert the curr of the qty
        df_rule_calc["qty_value"]=np.where(
          df_rule_calc["qty_value"]==0,
          "",
          df_rule_calc["qty_value"].astype(str)+df_rule_calc["qty_value_currency"] 
        )
        df_rule_calc=df_rule_calc.drop(["qty_value_currency"], axis = 1)
        df_rule_calc['period_from']=df_rule_calc['period_from'].astype(str)
        df_rule_calc['period_to']=df_rule_calc['period_to'].astype(str)
        df_rule_calc=df_rule_calc[['import_file_id','contract_id','year','contract_name','country_incl_excl','country_list','period_from','period_to','formulation','tranche_type','field_type','qty_value','sales_rate']]

        df_rule_calc.to_sql('royalty_app_rule_calc', con=conn, index=False, if_exists="append")
        print(df_rule_calc)
        print("df_rule_calc loaded succesfully")


        df_detail['import_file_id']=file.id
        df_detail.to_sql('royalty_app_detail', con=conn, index=False, if_exists="append")
        print("df_detail loaded succesfully")

        if file.file_type=="cash_forecast":
          df_cash_flow["import_file_id"]=file.id
          df_cash_flow.to_sql('royalty_app_cash_flow', con=conn, index=False, if_exists="append")
          print("df_cash_flow loaded succesfully")
          df_wht['import_file_id']=file.id
          df_wht.to_sql('royalty_app_wht', con=conn, index=False, if_exists="append")
          print("df_wht loaded succesfully")
        elif file.file_type=="accruals":
          df_conso['import_file_id']=file.id
          df_conso.to_sql('royalty_app_conso', con=conn, index=False, if_exists="append")
          print("df_conso loaded succesfully")
          df_gls['import_file_id']=file.id
          df_gls.to_sql('royalty_app_gls', con=conn, index=False, if_exists="append")
          print("df_gls loaded succesfully")
        elif file.file_type=="partner_report":
          df_sales_breakdown.to_sql('royalty_app_sales_breakdown_for_contract_report', con=conn, index=False, if_exists="append") 
          print("df_sales_breakdown loaded succesfully")
      except Exception as e:
        file.delete()
        return JsonResponse({"error": f"something went wrong with the import file- please check that the format is respected-   server message: {e}"}, status=201)
      return JsonResponse({"file_id": file.id,"date":file.date}, status=201)
    except: return JsonResponse({"error": "data not loaded"}, status=404)

@login_required
def export_report(request,file_array,table_array):
  file_nb_list=file_array.split(',')
  table_name_list=table_array.split(',')

  file_object_list=File.objects.filter(id__in=file_nb_list)

  with BytesIO() as b:
    # Use the StringIO object as the filehandle.
    writer = pd.ExcelWriter(b, engine='xlsxwriter')
    for table_name in table_name_list:

      if table_name =="sales":
        sales_list=Sale.objects.filter(import_file__in=file_object_list)
        df_sales = pd.DataFrame(list(sales_list.values()))
        df_sales=df_sales.drop(['id'], axis = 1)
        df_sales.to_excel(writer, sheet_name='Sales',index=False)

      if table_name=="fx":
        fx_list=Fx.objects.filter(import_file__in=file_object_list)
        df_fx = pd.DataFrame(list(fx_list.values()))
        df_fx=df_fx.drop(['id'], axis = 1)
        df_fx.to_excel(writer, sheet_name='Fx',index=False)

      if table_name=="rule":
        r_list=Rule_calc.objects.filter(import_file__in=file_object_list)
        df_rule_calc = pd.DataFrame(list(r_list.values()))
        df_rule_calc=df_rule_calc.drop(['id'], axis = 1)
        df_rule_calc.to_excel(writer, sheet_name='Rule',index=False)

      if table_name =="detail":
        detail_list=Detail.objects.filter(import_file__in=file_object_list)
        df_detail_list = pd.DataFrame(list(detail_list.values()))
        df_detail_list=df_detail_list.drop(['id'], axis = 1)
        df_detail_list.to_excel(writer, sheet_name='Detail',index=False)

      if table_name =="cash_flow":
        cash_flow_list=Cash_flow.objects.filter(import_file__in=file_object_list)
        df_cash_flow = pd.DataFrame(list(cash_flow_list.values()))
        df_cash_flow=df_cash_flow.drop(['id'], axis = 1)
        df_cash_flow.to_excel(writer, sheet_name='Cash_Flow',index=False)

      if table_name=="conso":
        conso_list=Conso.objects.filter(import_file__in=file_object_list)
        df_conso = pd.DataFrame(list(conso_list.values()))
        df_conso=df_conso.drop(['id'], axis = 1)
        df_conso.to_excel(writer, sheet_name='Conso',index=False)

      if table_name=="gls":
        gls_list=Gls.objects.filter(import_file__in=file_object_list)
        df_gls = pd.DataFrame(list(gls_list.values()))
        df_gls=df_gls.drop(['id'], axis = 1)
        df_gls.to_excel(writer, sheet_name='Accounting',index=False)

      if table_name =="wht":
        wht_list=Wht.objects.filter(import_file__in=file_object_list)
        df_wht = pd.DataFrame(list(wht_list.values()))
        df_wht=df_wht.drop(['id'], axis = 1)
        df_wht.to_excel(writer, sheet_name='WHT',index=False)

      
      if table_name=="sales_details":
        sales_details_list=Sales_breakdown_for_contract_report.objects.filter(import_file__in=file_object_list)
        df_sales_details= pd.DataFrame(list(sales_details_list.values()))
        df_sales_details=df_sales_details.drop(['id'], axis = 1)
        df_sales_details.to_excel(writer, sheet_name='sales_details',index=False)

    writer.save()

    # if there is only one file selected, we display a specific name- other wise we just list the files
    if len(file_nb_list)==1 :
      filename = f"{file_object_list[0].name}_{file_object_list[0].acc_year}/{file_object_list[0].acc_month}"
    else:
      filename =f"export mutliple files :{file_array}"

    content_type = 'application/vnd.ms-excel'
    response = HttpResponse(b.getvalue(), content_type=content_type)
    response['Content-Disposition'] = 'attachment; filename="' + filename + '.xlsx"'
    return response

#-------------------------------------
#----------Static Data ---------------
#-------------------------------------

@login_required(login_url='/login')
def modif_static(request,table_name):

  if table_name == "division" :
    country_list=Country.objects.all().order_by("country_id")
    division_list=Division.objects.all() 
    return render(request, 'royalty_app/division.html',  { "country_list":country_list ,"division_list":division_list})

  if table_name=="country":
    country_list=Country.objects.all().order_by("country_region","country_id").select_related('country_region')
    region_list=Region.objects.all()
    return render(request, 'royalty_app/country.html',  { "country_list":country_list ,"region_list":region_list})

  if table_name=="region":
    region_list=Region.objects.all()
    return render(request, 'royalty_app/region.html',  { "region_list":region_list})

  if table_name=="brand":
    brand_list=Brand.objects.all()
    return render(request, 'royalty_app/brand.html',  { "brand_list":brand_list})

  if table_name=="formulation":
    formulation_list=Formulation.objects.all()
    return render(request, 'royalty_app/formulation.html',  { "formulation_list":formulation_list})

  if table_name=="currency":
    currency_list=Currency.objects.all()
    return render(request, 'royalty_app/currency.html',  { "currency_list":currency_list})

  if table_name=="consolidation_currency":
    currency_list=Currency.objects.all()
    consolidation_currency=Consolidation_currency.objects.all().first()
    return render(request, 'royalty_app/consolidation_currency.html',  { "consolidation_currency":consolidation_currency,"currency_list":currency_list})

  if table_name=="accounting":
    accounting_list=Accounting.objects.all()
    return render(request, 'royalty_app/accounting.html',  { "accounting_list":accounting_list})

  if table_name=="tax":
    tax_list=Tax.objects.all().select_related('country_from','country_to')
    country_list=Country.objects.all()
    return render(request, 'royalty_app/tax.html',  { "country_list":country_list,"tax_list":tax_list})

  if table_name=="sales_breakdown_item":
    sales_breakdown_item_list=Sales_breakdown_item.objects.all()
    return render(request, 'royalty_app/sales_breakdown_item.html',  { "sales_breakdown_item_list":sales_breakdown_item_list})

  if table_name=="payment_type":
    payment_type_list=Payment_type.objects.all()
    return render(request, 'royalty_app/payment_type.html',  { "payment_type_list":payment_type_list})





@csrf_exempt
@login_required
def save_division(request):
  if request.method == "POST":
    #Save File
    try:
      data = json.loads(request.body)

      #delete all records that are not mention
      division_id_list=[]
      for d in data:
        division_id=d["division_id"]
        division_id_list.append(division_id)
      division_to_delete=Division.objects.exclude(division_id__in=division_id_list)
      
      division_to_delete.delete()

      for d in data :
        division_id=d["division_id"]
        
        country=Country.objects.get(country_id=d["division_country"])
        division_list_d=Division.objects.filter(division_id=division_id)
        
        #if the item already exist, we do modify it
        if len(division_list_d)==1:  

          division= division_list_d[0] 
          division.division_name=d["division_name"]
          division.division_country=country
          division.save()
        #if the item is new, we create it
        else:
          d=Division(
            division_id = division_id,
            division_name =d["division_name"],
            division_country=country,
          )
          d.save()
      return JsonResponse({"success": "data loaded"}, status=201)
    except Exception as e:
      return JsonResponse({"error": f"data not loaded-   server message: {e}"}, status=404)


@csrf_exempt
@login_required
def save_country(request):
  if request.method == "POST":
    #Save File
    try:
      data = json.loads(request.body)
      #delete all records that are not mention
      list_of_items_posted=[]
      for d in data:
        list_of_items_posted.append(d["country_id"])
      items_to_delete=Country.objects.exclude(country_id__in=list_of_items_posted)
      items_to_delete.delete()

      for d in data :
        country_id=d["country_id"]
        country=d["country"]
        country_region=Region.objects.get(id=d["country_region"])
        
        #if the item already exist, we modify it
        existing_items_equal_d=Country.objects.filter(country_id=country_id)
        if len(existing_items_equal_d)==1:  

          item_to_modify= existing_items_equal_d[0] 
          item_to_modify.country=country
          item_to_modify.country_region=country_region
          item_to_modify.save()
        #if the item is new, we create it
        else:
          mew_item=Country(
            country_id = country_id,
            country =country,
            country_region=country_region,
          )
          mew_item.save()
      return JsonResponse({"success": "data loaded"}, status=201)
    except Exception as e:
      return JsonResponse({"error": f"data not loaded-   server message: {e}"}, status=404)


@csrf_exempt
@login_required
def save_region(request):
  if request.method == "POST":
    #Save File
    try:
      data = json.loads(request.body)
      #delete all records that are not mention
      list_of_items_posted=[]
      for d in data:
        list_of_items_posted.append(d["region_id"])
      items_to_delete=Region.objects.exclude(id__in=list_of_items_posted)
      items_to_delete.delete()

      for d in data :
        region_id=d["region_id"]
        region_name=d["region_name"]
        
        #if the item already exist, we modify it
        existing_items_equal_d=Region.objects.filter(id=region_id)
        if len(existing_items_equal_d)==1:  
          item_to_modify= existing_items_equal_d[0] 
          item_to_modify.region=region_name
          item_to_modify.save()
        #if the item is new, we create it
        else:
          mew_item=Region(
            region =region_name,
          )
          mew_item.save()
      return JsonResponse({"success": "data loaded"}, status=201)
    except Exception as e:
      return JsonResponse({"error": f"data not loaded-   server message: {e}"}, status=404)


@csrf_exempt
@login_required
def save_brand(request):
  if request.method == "POST":
    #Save File
    try:
      data = json.loads(request.body)
      #delete all records that are not mention
      list_of_items_posted=[]
      for d in data:
        list_of_items_posted.append(d["brand_id"])
      items_to_delete=Brand.objects.exclude(id__in=list_of_items_posted)
      items_to_delete.delete()

      for d in data :
        brand_id=d["brand_id"]
        m3_brand_code=d["m3_brand_code"]
        brand_name=d["brand_name"]
        
        #if the item already exist, we modify it
        existing_items_equal_d=Brand.objects.filter(id=brand_id)
        if len(existing_items_equal_d)==1:  
          item_to_modify= existing_items_equal_d[0] 
          item_to_modify.m3_brand_code=m3_brand_code
          item_to_modify.brand_name=brand_name
          item_to_modify.save()
        #if the item is new, we create it
        else:
          mew_item=Brand(
            m3_brand_code =m3_brand_code,
            brand_name =brand_name,
          )
          mew_item.save()
      return JsonResponse({"success": "data loaded"}, status=201)
    except Exception as e:
      return JsonResponse({"error": f"data not loaded-   server message: {e}"}, status=404)


@csrf_exempt
@login_required
def save_formulation(request):
  if request.method == "POST":
    #Save File
    try:
      data = json.loads(request.body)
      #delete all records that are not mention
      list_of_items_posted=[]
      for d in data:
        list_of_items_posted.append(d["formula_code"])
      items_to_delete=Formulation.objects.exclude(formula_code__in=list_of_items_posted)

      items_to_delete.delete()

      for d in data :
        formula_code=d["formula_code"]
        formula_name=d["formula_name"]
        
        #if the item already exist, we modify it
        existing_items_equal_d=Formulation.objects.filter(formula_code=formula_code)
        if len(existing_items_equal_d)==1:  

          item_to_modify= existing_items_equal_d[0] 
          item_to_modify.formula_code=formula_code
          item_to_modify.formula_name=formula_name
          item_to_modify.save()
        #if the item is new, we create it
        else:
          mew_item=Formulation(
            formula_code = formula_code,
            formula_name =formula_name,
          )
          mew_item.save()
      return JsonResponse({"success": "data loaded"}, status=201)
    except Exception as e:
      return JsonResponse({"error": f"data not loaded-   server message: {e}"}, status=404)


@csrf_exempt
@login_required
def save_currency(request):
  if request.method == "POST":
    #Save File
    try:
      data = json.loads(request.body)

      #delete all records that are not mention
      list_of_items_posted=[]
      for d in data:
        list_of_items_posted.append(d["currency"])
      items_to_delete=Currency.objects.exclude(currency__in=list_of_items_posted)

      items_to_delete.delete()

      for d in data :
        currency=d["currency"]
        
        #if the item already exist, we modify it
        existing_items_equal_d=Currency.objects.filter(currency=currency)
        if len(existing_items_equal_d)==1:  

          item_to_modify= existing_items_equal_d[0] 
          item_to_modify.currency=currency
          item_to_modify.save()
        #if the item is new, we create it
        else:
          mew_item=Currency(
            currency = currency,
          )
          mew_item.save()
      return JsonResponse({"success": "data loaded"}, status=201)
    except Exception as e:
      return JsonResponse({"error": f"data not loaded-   server message: {e}"}, status=404)



@csrf_exempt
@login_required
def save_payment_type(request):
  if request.method == "POST":
    #Save File
    try:
      data = json.loads(request.body)

      #delete all records that are not mention
      list_of_items_posted=[]
      for d in data:
        list_of_items_posted.append(d["payment_type"])
      items_to_delete=Payment_type.objects.exclude(payment_type__in=list_of_items_posted)

      items_to_delete.delete()

      for d in data :
        payment_type=d["payment_type"]
        
        #if the item already exist, we modify it
        existing_items_equal_d=Payment_type.objects.filter(payment_type=payment_type)
        if len(existing_items_equal_d)==1:  

          item_to_modify= existing_items_equal_d[0] 
          item_to_modify.payment_type=payment_type
          item_to_modify.save()
        #if the item is new, we create it
        else:
          mew_item=Payment_type(
            payment_type = payment_type,
          )
          mew_item.save()
      return JsonResponse({"success": "data loaded"}, status=201)
    except Exception as e:
      return JsonResponse({"error": f"data not loaded-   server message: {e}"}, status=404)



@csrf_exempt
@login_required
def save_consolidation_currency(request):
  if request.method == "POST":
    #Save File
    try:
      data = json.loads(request.body)
      consolidation_currency=data["consolidation_currency"]
      rp=Consolidation_currency.objects.all().first()
      if rp == None:
        new_item=Consolidation_currency(
          currency= Currency.objects.get(currency=consolidation_currency) 
        )
        new_item.save()
      else:
        rp.currency= Currency.objects.get(currency=consolidation_currency )
        rp.save()


      return JsonResponse({"success": "data loaded"}, status=201)
    except Exception as e:
      return JsonResponse({"error": f"data not loaded-   server message: {e}"}, status=404)

@csrf_exempt
@login_required
def save_accounting(request):
  if request.method == "POST":
    #Save File
    try:
      data = json.loads(request.body)
      for d in data :
        accounting_id=d["accounting_id"]
        item_to_modify=Accounting.objects.get(id=accounting_id)

        
        item_to_modify.transaction_direction=d["transaction_direction"]
        item_to_modify.dim1=dim1=d["dim1"]
        item_to_modify.dim2=dim2=d["dim2"]
        item_to_modify.dim4=dim4=d["dim4"]
        item_to_modify.pl_bs=pl_bs=d["pl_bs"]
        item_to_modify.d_c_if_amount_positiv=d["d_c_if_amount_positiv"]
        item_to_modify.save()

      return JsonResponse({"success": "data loaded"}, status=201)
    except Exception as e:
      return JsonResponse({"error": f"data not loaded-   server message: {e}"}, status=404)

@csrf_exempt
@login_required
def save_tax(request):
  if request.method == "POST":
    #Save File
    try:
      data = json.loads(request.body)
      #delete all records
      Tax.objects.all().delete()

      for d in data :
        country_from=d["country_from"]
        country_to=d["country_to"]
        wht_rate=d["wht_rate"]

        new_item=Tax(
          country_from = Country.objects.get(country_id=country_from),
          country_to =Country.objects.get(country_id=country_to),
          wht_rate=wht_rate,
        )
        new_item.save()
      return JsonResponse({"success": "data loaded"}, status=201)
    except Exception as e:
      return JsonResponse({"error": f"data not loaded-   server message: {e}"}, status=404)


@csrf_exempt
@login_required
def save_sales_breakdown_item(request):
  if request.method == "POST":
    #Save File
    try:
      data = json.loads(request.body)
      #delete all records that are not mention
      list_of_items_posted=[]
      for d in data:
        list_of_items_posted.append(d["sales_breakdown_item_id"])
      items_to_delete=Sales_breakdown_item.objects.exclude(id__in=list_of_items_posted)
      items_to_delete.delete()

      for d in data :
        sales_breakdown_item_id=d["sales_breakdown_item_id"]
        sales_breakdown_definition=d["sales_breakdown_definition"]
        
        #if the item already exist, we modify it
        existing_items_equal_d=Sales_breakdown_item.objects.filter(id=sales_breakdown_item_id)
        if len(existing_items_equal_d)==1:  
          item_to_modify= existing_items_equal_d[0] 
          item_to_modify.sales_breakdown_definition=sales_breakdown_definition
          item_to_modify.save()
        #if the item is new, we create it
        else:
          mew_item=Sales_breakdown_item(
            sales_breakdown_definition =sales_breakdown_definition,
          )
          mew_item.save()
      return JsonResponse({"success": "data loaded"}, status=201)
    except Exception as e:
      return JsonResponse({"error": f"data not loaded-   server message: {e}"}, status=404)



      