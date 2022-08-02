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
  File,Sale, Rule_calc,Periodicity_cat,Consolidation_currency,Cash_flow,Detail,Accounting_entry,Conso,Wht,Sales_breakdown_for_contract_report,
  Contract_file,Month_table,User,Type,Milestone)
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

import time

import requests

#CAPTCHA
from royalty.settings.base import GOOGLE_RECAPTCHA_SITE_KEY,GOOGLE_RECAPTCHA_SECRET_KEY,DATABASE_URL_VIEW

# to create connection with database 
from sqlalchemy.engine.create import create_engine

@csrf_exempt
def isauthenticated(request):
  if request.user.is_authenticated:
    return  JsonResponse({"isauthenticated":"YES"}, status=201)
  else:
    return  JsonResponse({"isauthenticated":"NO"}, status=201)

import smtplib
def login_check(request):


  if request.user.is_authenticated:
    return HttpResponseRedirect(reverse("home")) 
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
          return render(request, "royalty_app/connection/login.html", {
            "error_message": error_message,
            'recaptcha_site_key':GOOGLE_RECAPTCHA_SITE_KEY
          })
          
      user = authenticate(request, username=username, password=password)
      # Check if authentication successful
      if user is not None:
        # if None, then it's a first time user, I should redirect him to a welcome page
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
        return render(request, "royalty_app/connection/login.html", {
            "error_message": ['Invalid username and/or password.'],
            'recaptcha_site_key':GOOGLE_RECAPTCHA_SITE_KEY
        })
    else:  
      return render(request, "royalty_app/connection/login.html",{'recaptcha_site_key':GOOGLE_RECAPTCHA_SITE_KEY,"error_message": ["Could not get Google CAPTCHA, please try again"]})
  else:
    return render(request, "royalty_app/connection/login.html",{'recaptcha_site_key':GOOGLE_RECAPTCHA_SITE_KEY})

def automatic_logout(request):
  return render(request, "royalty_app/connection/automatic_logout.html",{'recaptcha_site_key':GOOGLE_RECAPTCHA_SITE_KEY})

@csrf_exempt
@login_required(login_url='/login')
def new_profile_pict(request):
  if request.method == "POST":
    try:
      user=request.user
      user.profile_picture=request.FILES.get("file")
      user.save()
      return JsonResponse({"new_picture_url":user.profile_picture.url}, status=201)
    except Exception as e:
      return JsonResponse({"error": f"data not loaded-   server message: {e}"}, status=404)


def register(request):
  if request.user.is_authenticated:
    return HttpResponseRedirect(reverse("home")) 
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
      print("Captcha OK")
      username = request.POST["email"]
      email = request.POST["email"]
      first_name = request.POST["first_name"]
      last_name = request.POST["last_name"]

      # Ensure password matches confirmation
      password = request.POST["password"]
      confirmation = request.POST["confirmation"]
      if password != confirmation:
          return render(request, "royalty_app/connection/register.html", {
              "error_message": ["Passwords must match."],'recaptcha_site_key':GOOGLE_RECAPTCHA_SITE_KEY
          })
      print("password OK")
      if User.objects.filter(email=email):
          return render(request, "royalty_app/connection/register.html", {
              "error_message": ["Email already exists"],'recaptcha_site_key':GOOGLE_RECAPTCHA_SITE_KEY
          })
      print("New email OK")
      try: 
        password_validation.validate_password(password, request)
      except Exception as e:
        return render(request, "royalty_app/connection/register.html",{
          "error_message":e ,'recaptcha_site_key':GOOGLE_RECAPTCHA_SITE_KEY}
          )
      print("password and email OK")
      # Attempt to create new user
      try:
        user = User.objects.create_user(username, email, password)
        #user = get_user_model().objects.create(username=username, password=password, email=email)
        user.first_name=first_name
        user.last_name=last_name
        user.is_active = False
        user.save()
        send_email(user)
        print("email sent")
        return render(request, "royalty_app/connection/register.html", {"message_confirmation": "email for confimation has been sent",'recaptcha_site_key':GOOGLE_RECAPTCHA_SITE_KEY})    
      except IntegrityError:
        return render(request, "royalty_app/connection/register.html", {"error_message": ["Username already taken"],'recaptcha_site_key':GOOGLE_RECAPTCHA_SITE_KEY})
    else:
      return render(request, "royalty_app/connection/register.html",{"error_message": ["CAPTCHA must be validated"],'recaptcha_site_key':GOOGLE_RECAPTCHA_SITE_KEY})
  else:
    return render(request, "royalty_app/connection/register.html",{'recaptcha_site_key':GOOGLE_RECAPTCHA_SITE_KEY})



@login_required(login_url='/login')
def logout_view(request):
  logout(request)
  return HttpResponseRedirect(reverse("home"))    





@login_required(login_url='/login')
def home(request):

    #---------------calculation for Accruals graph------------
    current_year=datetime.now().year
    accruals_file_list=File.objects.filter(file_type="accruals",dashboard=True)

    # contract_nb and partner_nb:
    contract_nb=len(Contract.objects.filter(status__in=['CHANGE','DELETE','CURRENT']))
    partner_nb=len(Partner.objects.filter(status__in=['CHANGE','DELETE','CURRENT']))
    #year list
    accruals_year_list=accruals_file_list.values_list('acc_year')
    accruals_year_list=list(dict.fromkeys(accruals_year_list))
    accruals_year_list=[int(y[0]) for y in accruals_year_list]
    #contract Type list
    detail_queryset=Detail.objects.filter(import_file__in = accruals_file_list)
    accruals_contract_type_list=Type.objects.filter(detail__in=detail_queryset).distinct().values_list('name')
    accruals_contract_type_list=[y[0] for y in accruals_contract_type_list]
    #if the current year does not exist, insert it in the list
    if current_year not in accruals_year_list:
      accruals_year_list.append(current_year)
    accruals_year_list.sort()

    consolidation_currency=Consolidation_currency.objects.all().first()
    accruals_contract_list=Contract.objects.filter(detail__in=detail_queryset).distinct().order_by('id')
    accruals_contract_id_list=accruals_contract_list.values_list('id')
    accruals_contract_id_list=[c[0] for c in accruals_contract_id_list]

    result=chart_accruals(current_year,accruals_contract_id_list,accruals_contract_type_list)
    accruals_labels=result[0]
    accruals_data=result[1]
    accruals_data_roy_ytd=result[2]

    result=chart_accruals(current_year-1,accruals_contract_id_list,accruals_contract_type_list)
    accruals_data_last_year=result[1]
    accruals_data_roy_ytd_last_year=result[2]
    
  #---------------calculation for CFF graph------------
    CFF_file_list=File.objects.filter(file_type="cash_forecast",dashboard=True)
    #year list
    CFF_year_list=Cash_flow.objects.exclude(rule_type="INVOICE").filter(import_file__in=CFF_file_list).values_list('payment_date__year')
    CFF_year_list=list(dict.fromkeys(CFF_year_list))
    CFF_year_list=[int(y[0]) for y in CFF_year_list]
    #contract Type list
    CFF_contract_type_list=Type.objects.filter(detail__in=Detail.objects.filter(import_file__in = CFF_file_list).exclude(rule_type="INVOICE")).distinct().values_list('name')
    CFF_contract_type_list=[y[0] for y in CFF_contract_type_list]
    CFF_currency_list=Currency.objects.filter(cash_flow__in=Cash_flow.objects.filter(import_file__in = CFF_file_list).exclude(rule_type="INVOICE")).distinct().values_list('currency')
    CFF_currency_list=[y[0] for y in CFF_currency_list]
    #contract list
    CFF_contract_list=Contract.objects.filter(detail__in=Detail.objects.filter(import_file__in = CFF_file_list).exclude(rule_type="INVOICE")).distinct().order_by('id')
    CFF_contract_id_list=CFF_contract_list.values_list('id')
    CFF_contract_id_list=[c[0] for c in CFF_contract_id_list]
    
    #get the label, data as well as the
    result=chart_cash_forecast(current_year,CFF_contract_type_list,CFF_currency_list,CFF_contract_id_list)
    CFF_labels=result[0]
    CFF_data=result[1] 
    #data for countract pies
    CFF_labels_contract=result[2]
    CFF_data_contract=result[3]
    CFF_color_contract=result[4]
    # data for country pie
    CFF_labels_country=result[5]
    CFF_data_country=result[6]
    CFF_color_country=result[7]
    # data for currency pie
    CFF_labels_currency=result[8]
    CFF_data_currency=result[9]
    CFF_color_currency=result[10]

    #previous year for bar chart
    result=chart_cash_forecast(current_year-1,CFF_contract_type_list,CFF_currency_list,CFF_contract_id_list)
    CFF_data_last_year=result[1] 

    print("contact")
    return render(request, 'royalty_app/home.html', {
      "current_year":current_year,
      "contract_nb":contract_nb,
      "partner_nb":partner_nb,
      "consolidation_currency":consolidation_currency,

      "CFF_total_amount":round(sum(CFF_data_country)/1000000,2),
      "CFF_labels_currency":CFF_labels_currency,"CFF_data_currency":CFF_data_currency,"CFF_color_currency":CFF_color_currency,
      "CFF_labels_country":CFF_labels_country,"CFF_data_country":CFF_data_country,"CFF_color_country":CFF_color_country,
      "CFF_labels_contract":CFF_labels_contract,"CFF_data_contract":CFF_data_contract,"CFF_color_contract":CFF_color_contract,
      "CFF_currency_list":CFF_currency_list,"CFF_year_list":CFF_year_list,
      "CFF_contract_type_list":CFF_contract_type_list,
      "CFF_data_last_year":CFF_data_last_year,
      "CFF_data":CFF_data,
      "CFF_labels":CFF_labels,
      "CFF_contract_list":CFF_contract_list,
      "CFF_contract_id_list":CFF_contract_id_list,
      "accruals_contract_type_list":accruals_contract_type_list,
      "accruals_data_last_year":accruals_data_last_year,
      "accruals_data_roy_ytd_last_year":accruals_data_roy_ytd_last_year,
      "accruals_contract_id_list":accruals_contract_id_list,
      "accruals_contract_list":accruals_contract_list,
      "accruals_labels":accruals_labels,
      "accruals_data":accruals_data,
      "accruals_data_roy_ytd":accruals_data_roy_ytd,
      "accruals_year_list":accruals_year_list
      })



def chart_cash_forecast(year,contract_type_list,currency_list,contract_id_list):

  CFF_report_list=File.objects.filter(file_type="cash_forecast").filter(dashboard=True)
  detail_list=Detail.objects.exclude(rule_type="INVOICE").filter(contract__id__in=contract_id_list,contract_type__name__in=contract_type_list,import_file__in=CFF_report_list,payment_currency__in=currency_list,payment_date__year=year).values_list('payment_date','amount_consolidation_curr','rule_type','transaction_direction','contract__contract_name','market_id','payment_currency')


  if not detail_list :

    labels_bar_chart=[ "Jan", "Feb", "Mar", "Apr", "Mai", "Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    data_bar_chart=[0,0,0,0,0,0,0,0,0,0,0,0]
    labels_contract=["NA"]
    data_contract=[0]
    color_contract=['rgba(255, 177, 193,1)']
    labels_country=["NA"]
    data_country=[0]
    color_country=['rgba(255, 177, 193,1)']
    labels_currency=["NA"]
    data_currency=[0]
    color_currency=['rgba(255, 177, 193,1)']
  else:
    df_detail_list=pd.DataFrame.from_records(list(detail_list), columns=['payment_date','amount_consolidation_curr','rule_type','transaction_direction','contract','market_id','payment_currency'])
    print("cash data retreival: 3")
    #data for bar
    df_data=df_detail_list.groupby(['payment_date','rule_type','transaction_direction','contract','market_id','payment_currency'], as_index=False).agg({"amount_consolidation_curr": "sum"})

    df_data['payment_month'] =  pd.DatetimeIndex(df_data['payment_date']).month
    df_data['payment_month'] = df_data['payment_month'].astype(int)
    df_data=df_data.drop(['payment_date'], axis = 1)  

    df_data=df_data.rename(columns={'amount_consolidation_curr':'amount'})
  

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

    df_pie=df_data.copy()
    df_data=pd.merge(df_month,df_data,how="left",left_on=["month_nb"],right_on=["payment_month"])
    df_data=df_data.groupby(['month_nb','month'], as_index=False,dropna=False).agg({"amount": "sum"})
    df_data=df_data.sort_values(['month_nb'], ascending=[1])
    df_data=df_data.drop(['month_nb'], axis = 1)
    df_data=df_data.fillna("0")
    datas=df_data.values.tolist()
    labels_bar_chart=[ d[0] for d in datas]
    data_bar_chart=[ d[1] for d in datas]

    #-------- pie contract
    df_contract_pie=df_pie.groupby(['contract'], as_index=False).agg({"amount": "sum"}).sort_values(by=['amount'],ascending=False)
    datas=df_contract_pie.values.tolist()
    labels_contract=[]
    data_contract=[]
    color_contract=[]
    nb_items=min(len(datas),10)
    t=1
    small_value=0
    for data in datas:
      if t>9 :
        small_value=data[1]+small_value
        transparance=1/nb_items
        color= f'rgba(255, 177, 193,{transparance})'
      else:  
        transparance=(nb_items-t+1)/nb_items
        t=t+1
        color= f'rgba(255, 177, 193,{transparance})'
        color_contract.append(color)
        labels_contract.append(data[0][:15] + (data[0][15:] and '..'))
        data_contract.append(round(data[1],0))
    if small_value!=0:
      labels_contract.append('other')
      data_contract.append(round(small_value,0))
      color_contract.append(color)
    #---------------- pie country------------
    df_country_pie=df_pie.groupby(['market_id'], as_index=False).agg({"amount": "sum"}).sort_values(by=['amount'],ascending=False)

    datas=df_country_pie.values.tolist()

    labels_country=[]
    data_country=[]
    color_country=[]
    nb_items=min(len(datas),10)
    t=1
    small_value=0
    for data in datas:
      if t>9 :
        small_value=data[1]+small_value
        transparance=1/nb_items
        color= f'rgba(255, 177, 193,{transparance})'
      else:  
        transparance=(nb_items-t+1)/nb_items
        t=t+1
        color= f'rgba(255, 177, 193,{transparance})'
        color_country.append(color)
        labels_country.append(data[0])
        data_country.append(round(data[1],0))
    if small_value!=0:
      labels_country.append('other')
      data_country.append(round(small_value,0))
      color_country.append(color)
    #---------------- pie currency------------
    df_currency_pie=df_pie.groupby(['payment_currency'], as_index=False).agg({"amount": "sum"}).sort_values(by=['amount'],ascending=False)
    datas=df_currency_pie.values.tolist()

    labels_currency=[]
    data_currency=[]
    color_currency=[]
    nb_items=min(len(datas),10)
    t=1
    small_value=0
    for data in datas:
      if t>9 :
        small_value=data[1]+small_value
        transparance=1/nb_items
        color= f'rgba(255, 177, 193,{transparance})'
      else:  
        transparance=(nb_items-t+1)/nb_items
        t=t+1
        color= f'rgba(255, 177, 193,{transparance})'
        color_currency.append(color)
        labels_currency.append(data[0])
        data_currency.append(round(data[1],0))
    if small_value!=0:
      labels_currency.append('other')
      data_currency.append(round(small_value,0))
      color_currency.append(color)
  print("finish cash flow retreival")
  return [labels_bar_chart, data_bar_chart,labels_contract,data_contract,color_contract,labels_country,data_country,color_country,labels_currency,data_currency,color_currency]




@csrf_exempt
@login_required(login_url='/login')
def accruals_change(request):
  if request.method == "POST":
    #Save File
    try:
      data = json.loads(request.body)

      year=int(data["year"])

      contract_list=data["contract_list"]
      if   contract_list ==['']:
        contract_list=["0"]

      contract_type_list=data["contract_type_list"]
      if   contract_type_list ==['']:
        contract_type_list=["0"]

      result=chart_accruals(year,contract_list,contract_type_list)
      data_accruals=result[1]
      data_roy_ytd=result[2] 

      result=chart_accruals(year-1,contract_list,contract_type_list)
      data_accruals_last_year=result[1]
      data_roy_ytd_last_year=result[2] 
      
      return JsonResponse({"success": "data loaded","data_accruals_last_year":data_accruals_last_year,"data_roy_ytd_last_year":data_roy_ytd_last_year,"data_accruals":data_accruals,"data_roy_ytd":data_roy_ytd}, status=201)
    except Exception as e:
      return JsonResponse({"error": f"data not loaded-   server message: {e}"}, status=404)

@csrf_exempt
@login_required(login_url='/login')
def cash_forecast_change(request):
  if request.method == "POST":
    #Save File
    try:
      data = json.loads(request.body)

      year=int(data["year"])
      currency_list=data["currency_list"]
      if   currency_list ==['']:
        currency_list=["0"]


      contract_type_list=data["contract_type_list"]
      if   contract_type_list ==['']:
        contract_type_list=["0"]

      CFF_contract_id_list=data["CFF_contract_id_list"]
      if   CFF_contract_id_list ==['']:
        CFF_contract_id_list=["0"]


 
      result=chart_cash_forecast(year,contract_type_list,currency_list,CFF_contract_id_list)
 
      data_cash_forecast=result[1] 
      #data for countract pies
      labels_contract=result[2]
      data_contract=result[3]
      color_contract=result[4]
      # data for country pie
      labels_country=result[5]
      data_country=result[6]
      color_country=result[7]
      # data for currency pie
      labels_currency=result[8]
      data_currency=result[9]
      color_currency=result[10]


      result=chart_cash_forecast(year-1,contract_type_list,currency_list,CFF_contract_id_list)
      data_cash_forecast_last_year=result[1] 

      return JsonResponse({
        "success": "data loaded",
        "total_amount":round(sum(data_country)/1000000,2),
        "labels_currency":labels_currency,"data_currency":data_currency,"color_currency":color_currency,
        "labels_country":labels_country,"data_country":data_country,"color_country":color_country,
        "labels_contract":labels_contract,"data_contract":data_contract,"color_contract":color_contract,
        "data_cash_forecast":data_cash_forecast,"data_cash_forecast_last_year":data_cash_forecast_last_year,}, status=201)
    except Exception as e:
      return JsonResponse({"error": f"data not loaded-   server message: {e}"}, status=404)




def chart_accruals(year,contract_id_list,contract_type_list):
  #-----------Default Chart JS-----------
  #create the list of available year
  print("chart_accruals 0")

  file_list=File.objects.filter(file_type="accruals").filter(acc_year=year).filter(dashboard=True)
  
  df_file_list=pd.DataFrame(list(file_list.values()))
  if not file_list :
    labels=[ "Jan", "Feb", "Mar", "Apr", "Mai", "Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    data_accruals=[0,0,0,0,0,0,0,0,0,0,0,0]
    data_roy_ytd=[0,0,0,0,0,0,0,0,0,0,0,0]
  else:
    print("chart_accruals 1")
    #import detail tab:
    detail_list=Detail.objects.filter(contract_type__name__in=contract_type_list,import_file__in=file_list,contract_id__in=contract_id_list ).values_list('import_file_id','year_of_sales','amount_consolidation_curr','rule_type','transaction_direction')
    df_detail_list=pd.DataFrame.from_records(list(detail_list), columns=['import_file_id','year_of_sales','amount_consolidation_curr','rule_type','transaction_direction'])
    df_detail_list=df_detail_list.groupby(['import_file_id','year_of_sales','rule_type','transaction_direction'], as_index=False).agg({"amount_consolidation_curr": "sum"})
    print("chart_accruals 2")
    #merge file and detail:
    df_data=pd.merge(df_file_list,df_detail_list, how="inner",left_on=['id'], right_on=['import_file_id'] )
    df_data["amount_consolidation_curr"]=df_data["amount_consolidation_curr"].round(decimals=0)   
    
    #Creation of Accruals column
    df_data["Accruals"]=np.where(
      df_data["rule_type"]=="INVOICE",
      -df_data["amount_consolidation_curr"],
      df_data["amount_consolidation_curr"]
    )
    print("chart_accruals 3")
    df_data["Accruals"]=np.where(
      df_data["transaction_direction"]=="REC",
      -df_data["Accruals"],
      df_data["Accruals"]
    )
    #Creation of Ytd column
    print("chart_accruals 4")

    df_data["Ytd_roy"]=np.where(
      df_data["year_of_sales"]==df_data["acc_year"],
      np.where(
        df_data["rule_type"]=="INVOICE",
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


  #API to change role- only in test environment:
@login_required(login_url='/login')
def change_role(request):
  user=request.user
  if user.role=="WRITER" :
    user.role="VALIDATOR"
  else:
    user.role="WRITER"
  user.save()
  return HttpResponseRedirect(reverse("home"))

  #-----------------------------------PARTNER START----------------------------
  #----------------------------------------------------------------------------
@login_required(login_url='/login')
def partners(request):
  user=request.user
  partner_list_validated=Partner.objects.filter(status__in=["CURRENT","CHANGE","DELETE"]).select_related('partner_country','partner_payment_type')
  payment_type_list=Payment_type.objects.all()
  region_list=Region.objects.all()
  country_list=Country.objects.all().order_by("country").select_related('country_region')

  if user.role=="WRITER" :
    partner_list_writer=Partner.objects.filter(status__in=["CURRENT","NEW","CHANGE","DELETE"]).select_related('partner_country','partner_payment_type','partner_proposal')
    for p in partner_list_writer:
      if p.status=="CHANGE" :
        partner_proposal=p.partner_proposal
        p.partner_name= partner_proposal.partner_name
        p.partner_m3_code= partner_proposal.partner_m3_code
        p.partner_country= partner_proposal.partner_country
        p.partner_bank_account= partner_proposal.partner_bank_account
        p.partner_payment_type= partner_proposal.partner_payment_type
        p.ico_3rd= partner_proposal.ico_3rd
    return render(request, 'royalty_app/partners/partners.html',  {"partner_list_validated":partner_list_validated, "payment_type_list":payment_type_list,"partner_list_writer":partner_list_writer, "country_list":country_list ,"region_list":region_list})
 
  elif user.role=="VALIDATOR":
    partner_list_to_validate=Partner.objects.all().filter(status__in=["CHANGE","DELETE","NEW"]).select_related('partner_country','partner_payment_type')
    for p in partner_list_to_validate:
      if p.status=="CHANGE" :
        partner_proposal=p.partner_proposal
        p.partner_name= partner_proposal.partner_name
        p.partner_m3_code= partner_proposal.partner_m3_code
        p.partner_country= partner_proposal.partner_country
        p.partner_bank_account= partner_proposal.partner_bank_account
        p.partner_payment_type= partner_proposal.partner_payment_type
        p.ico_3rd= partner_proposal.ico_3rd

    return render(request, 'royalty_app/partners/partners.html',  {"partner_list_to_validate":partner_list_to_validate,"partner_list_validated":partner_list_validated, "payment_type_list":payment_type_list, "country_list":country_list ,"region_list":region_list})
  elif user.role=="READER":
    return render(request, 'royalty_app/partners/partners.html',  {"partner_list_validated":partner_list_validated, "payment_type_list":payment_type_list, "country_list":country_list ,"region_list":region_list})
  else :
    return HttpResponseRedirect(reverse("home"))

@csrf_exempt 
@login_required(login_url='/login')
def validate_new_partner(request,partner_id):

  user=request.user
  if user.role=="VALIDATOR": 
    partner=Partner.objects.get(id=partner_id)
    if request.method == "POST" and partner.status != "CURRENT":
      try:
        partner.status="CURRENT"
        partner.save()
        return JsonResponse({"result": "all done"}, status=201)
      except ProtectedError as e:
        message=f"{e}"
        message=message.replace('(', '').replace(')', '')
        return JsonResponse({"error": message}, status=400)
    else:
      return JsonResponse({"error": "GET or PUT request required."}, status=400)
  else:
    return JsonResponse({"error": "as a non VALIDATOR, you do not have the right to perform that task"}, status=400)
@csrf_exempt 
@login_required(login_url='/login')
def validate_change_partner(request,partner_id):

  user=request.user
  if user.role=="VALIDATOR": 
    partner=Partner.objects.get(id=partner_id)
    partner_proposal=partner.partner_proposal
    if request.method == "POST" and partner.status != "CURRENT":
      try:
        partner.partner_name=partner_proposal.partner_name
        partner.partner_m3_code=partner_proposal.partner_m3_code
        partner.partner_country=partner_proposal.partner_country
        partner.partner_bank_account= partner_proposal.partner_bank_account
        partner.partner_payment_type=partner_proposal.partner_payment_type
        partner.ico_3rd= partner_proposal.ico_3rd
        partner.partner_proposal=None
        partner.status="CURRENT"
        partner.save()

        partner_proposal.delete()

        return JsonResponse({"result": "all done"}, status=201)
      except ProtectedError as e:
        message=f"{e}"
        message=message.replace('(', '').replace(')', '')
        return JsonResponse({"error": message}, status=400)
    else:
      return JsonResponse({"error": "GET or PUT request required."}, status=400)
  else:
    return JsonResponse({"error": "as a non VALIDATOR, you do not have the right to perform that task"}, status=400)

@csrf_exempt 
@login_required(login_url='/login')
def reject_change_partner(request,partner_id):

  user=request.user
  if user.role=="VALIDATOR": 
    partner=Partner.objects.get(id=partner_id)
    partner_proposal=partner.partner_proposal
    if request.method == "POST"and partner.status != "CURRENT":
      try:

        partner.status="CURRENT"
        partner.partner_proposal=None
        partner.save()

        partner_proposal.delete()

        return JsonResponse({"result": "all done"}, status=201)
      except ProtectedError as e:
        message=f"{e}"
        message=message.replace('(', '').replace(')', '')
        return JsonResponse({"error": message}, status=400)
    else:
      return JsonResponse({"error": "GET or PUT request required."}, status=400)
  else:
    return JsonResponse({"error": "as a non VALIDATOR, you do not have the right to perform that task"}, status=400)

@csrf_exempt 
@login_required(login_url='/login')
def delete_partner(request,partner_id):
  user=request.user
  if user.role=="VALIDATOR": 
    if request.method == "POST":
      try:
        partner=Partner.objects.get(pk=partner_id)
        if  partner.status!="CURRENT" :
          partner.delete()
          return JsonResponse({"result": "all done"}, status=201)
        else:
          return JsonResponse({"error": "item should not be in CURRENT status"}, status=400) 
      except ProtectedError as e:
        message=f"{e}"
        message=message.replace('(', '').replace(')', '')
        return JsonResponse({"error": message}, status=400)
      except:
        return JsonResponse({"error": "something went wrong"}, status=400) 
    else:
      return JsonResponse({"error": "GET or PUT request required."}, status=400)
  else:
    return JsonResponse({"error": "as a non VALIDATOR, you do not have the right to perform that task"}, status=400)

  #  Tasks perform by writer
@csrf_exempt 
@login_required(login_url='/login')
def change_row(request,partner_id):
  user=request.user
  if user.role=="WRITER": 
    try:
      partner = Partner.objects.get( id=partner_id)
    except partner.DoesNotExist:
      return JsonResponse({"error": "post not found."}, status=404)

    if request.method == "POST" and partner.status=="CURRENT" :
      data = json.loads(request.body)
      
      partner_proposal=Partner(
        partner_m3_code = data["partner_m3_code"],
        partner_name = data["partner_name"],
        ico_3rd = data["ico_3rd"],
        partner_country=Country.objects.get(country_id=data["country_id"]),
        partner_bank_account = data["partner_bank_account"],
        partner_payment_type=Payment_type.objects.get(id=data["partner_payment_type_id"]),
        status='PROPOSAL'      
      )
      partner_proposal.save()

      partner.partner_proposal=partner_proposal
      partner.status='CHANGE'
      partner.save()
      return JsonResponse({"result": "all done"}, status=201)
    else:
      return JsonResponse({"error": "GET or PUT request required."}, status=400)
  else:
    return JsonResponse({"error": "as a non WRITER, you do not have the right to perform that task"}, status=400)

@login_required(login_url='/login')
def cancel_row_partner(request,partner_id):
  try:
    partner = Partner.objects.get( id=partner_id)
  except partner.DoesNotExist:
    return JsonResponse({"error": "post not found."}, status=404)

  if request.method == "GET" :
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
@login_required(login_url='/login')
def delete_row_partner(request,partner_id):
  user=request.user
  if user.role=="WRITER":
    if request.method == "POST" :
      try:
        partner=Partner.objects.get(pk=partner_id)
        if  partner.status=="CURRENT" :
          #We verify that the partner is not already used in a contract
          contract_partners=Contract_partner.objects.filter(partner=partner)
          if contract_partners: 
            df_contract_partner = pd.DataFrame(list(contract_partners.values())).drop_duplicates(subset=['contract_id'])
            contracts=Contract.objects.all()
            df_contract=pd.DataFrame(list(contracts.values()))
            df_contract_partner=pd.merge(df_contract_partner,df_contract, how="inner",left_on=['contract_id'], right_on=['id'] )[['contract_name']]
            df_contract_partner=df_contract_partner.values.tolist()
            contract_list=','.join([y[0] for y in df_contract_partner])
            return JsonResponse({"error": f'You cannot delete this partner, as it is already used in the following contract(s):{contract_list} '}, status=404)

          #We verify that the partner is not already used in a report
          details=Detail.objects.filter(partner=partner)
          if details: 
            df_detail = pd.DataFrame(list(details.values())).drop_duplicates(subset=['import_file_id'])
            files=File.objects.all()
            df_file=pd.DataFrame(list(files.values()))
            df_detail=pd.merge(df_detail,df_file, how="inner",left_on=['import_file_id'], right_on=['id'] )[['name']]
            df_detail=df_detail.values.tolist()
            report_list=','.join([y[0] for y in df_detail])
            return JsonResponse({"error": f'You cannot delete this partner, as it is already used in the following report(s):{report_list} -please delete them first '}, status=404)

          partner.status="DELETE"
          partner.save()
          return JsonResponse({"result": "all done"}, status=201)
        else:
          return JsonResponse({"error": "item not in CURRENT status"}, status=400)  
      except ProtectedError as e:
        message=f"{e}"
        message=message.replace('(', '').replace(')', '')
        return JsonResponse({"error": message}, status=400)
    else:
      return JsonResponse({"error": "GET or PUT request required."}, status=400)
  else:
    return JsonResponse({"error": "as a non WRITER, you do not have the right to perform that task"}, status=400)


@csrf_exempt 
@login_required(login_url='/login')
def new_partner(request):
  user=request.user
  if user.role=="WRITER":
    if request.method == "POST" :
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
  else:
    return JsonResponse({"error": "as a non WRITER, you do not have the right to perform that task"}, status=400)

  #-----------------------------------PARTNER END----------------------------
  #----------------------------------------------------------------------------

@login_required(login_url='/login')
def contracts_writer(request):
  user=request.user
  if user.role!="WRITER":
    return HttpResponseRedirect(reverse("contracts_current")) 
  else:
    contract_list=Contract.objects.filter(status__in=['IN_CREATION','CHANGE','NEW','DELETE','CURRENT']).select_related('m3_brand','division','division_via','payment_periodicity','minimum_guar_remaining_allocation_country','contract_currency','contract_type')
    for c in contract_list:
      if c.status=="CHANGE" :
        contract_proposal=c.contract_proposal
        c.contract_name= contract_proposal.contract_name
        c.transaction_direction= contract_proposal.transaction_direction
        c.division= contract_proposal.division
        c.division_via= contract_proposal.division_via
        c.contract_currency= contract_proposal.contract_currency
        c.payment_periodicity= contract_proposal.payment_periodicity
        c.payment_terms= contract_proposal.payment_terms
        c.m3_brand= contract_proposal.m3_brand
        c.mini_gar_status= contract_proposal.mini_gar_status
        c.mini_gar_from= contract_proposal.mini_gar_from
        c.mini_gar_to= contract_proposal.mini_gar_to

    region_list=Region.objects.all()
    country_list=Country.objects.all().select_related('country_region')
    m3_brand_list=Brand.objects.all().order_by("brand_name")
    division_list=Division.objects.all()
    currency_list=Currency.objects.all()
    periodicity_list=Periodicity.objects.all()
    type_list=Type.objects.all()

    return render(request, 'royalty_app/contracts/writer/contracts_writer.html',  {"type_list":type_list,"periodicity_list":periodicity_list,"currency_list":currency_list,"division_list":division_list,"m3_brand_list":m3_brand_list, "contract_list":contract_list,"region_list":region_list, "country_list":country_list})


@login_required(login_url='/login')
def delete_contract(request,contract_id):
  Contract.objects.get(id=contract_id).delete()
  return HttpResponseRedirect(reverse("contracts_writer")) 

@csrf_exempt 
@login_required(login_url='/login')
def submit_delete_contract_request(request,contract_id):
  user=request.user
  if user.role=="WRITER":
    contract=Contract.objects.get(id=contract_id)
    #we must verify that the contract is not used in any of the reports
    details=Detail.objects.filter(contract=contract)

    if details: 
      df_detail = pd.DataFrame(list(details.values())).drop_duplicates(subset=['import_file_id'])
      files=File.objects.all()
      df_file=pd.DataFrame(list(files.values()))
      df_detail=pd.merge(df_detail,df_file, how="inner",left_on=['import_file_id'], right_on=['id'] )[['name']]
      df_detail=df_detail.values.tolist()
      report_list=','.join([y[0] for y in df_detail])

      return JsonResponse({"error": f'You cannot delete this contract, as it is already used in the following report(s):{report_list} - please delete those reports first'}, status=404)
    contract.status="DELETE"
    contract.save()
    return HttpResponseRedirect(reverse("contracts_writer"))  
  else:
    return JsonResponse({"error": "you are not a writer"}, status=404)
    

@login_required(login_url='/login')
def contracts_current(request):
  contract_list=Contract.objects.filter(status__in=['CHANGE','DELETE','CURRENT']).select_related('m3_brand','division','division_via','payment_periodicity','minimum_guar_remaining_allocation_country','contract_currency')
  contract_list_to_validate=Contract.objects.all().filter(status__in=["PROPOSAL","NEW","DELETE"])
  message_validator=f'you have {len(contract_list_to_validate)} request(s) to validate'
  return render(request, 'royalty_app/contracts/current/contracts_current.html',  {"contract_list":contract_list,"message_validator":message_validator})

@login_required(login_url='/login')
def contracts_to_validate(request):

  contract_list=Contract.objects.filter(status__in=['PROPOSAL','DELETE','NEW']).select_related('m3_brand','division','division_via','payment_periodicity','minimum_guar_remaining_allocation_country','contract_currency')
  print(len(contract_list))
  for c in contract_list :
    if c.status=="PROPOSAL":
      try: #in case several "contracts_to_validate" are launched
        original_id=Contract.objects.get(contract_proposal=c).id
        c.pk=original_id
      except:
        pass
      c.status="CHANGE"

  contract_list_to_validate=Contract.objects.all().filter(status__in=["PROPOSAL","NEW","DELETE"])
  return render(request, 'royalty_app/contracts/validator/contracts_validator.html',  {"contract_list":contract_list})

@login_required(login_url='/login')
def rules(request,contract_id):
  #----------------------------------------------------------------------
  #------------list for WRITER/VALIDATOR and REARDER---------------------
  #----------------------------------------------------------------------

    user=request.user
    contract=Contract.objects.get(id=contract_id)
    #       Info for WRITER page
    formulation_list=Formulation.objects.all()
    region_list=Region.objects.all().order_by("region")
    country_list=Country.objects.all().order_by("country_id").select_related('country_region')
    partner_list=Partner.objects.all().filter(status__in=['CHANGE','DELETE','CURRENT']).order_by("partner_name")
    currency_list=Currency.objects.all()
    periodicity_list=Periodicity.objects.all()
    division_list=Division.objects.all()
    brand_list=Brand.objects.all().order_by("brand_name")
    #       Info for WRITER, VALIDATE, PENDING_VALIDATION page
    milestone_list=Milestone.objects.filter(contract=contract).select_related('currency')
    attachement_list=Contract_file.objects.filter(contract=contract)
    rule_list=Rule.objects.filter(contract=contract).select_related('qty_value_currency','tranche_currency')
    tranche_list=Tranche.objects.filter(rule__in=rule_list).order_by("id").select_related('rule')
    contract_partner_list=Contract_partner.objects.filter(contract=contract)
    if contract.contract_type.name=="MARGIN_ADJ":
      for r in rule_list :
        if r.rule_type != "SALES":
          print(r.qty_value)
          r.qty_value=abs(r.qty_value)
          r.rate_value=abs(r.rate_value)
          print(r.qty_value)
      for t in tranche_list:
        t.percentage=abs(t.percentage) 

    return_page='royalty_app/contracts/current/rules.html'

    rule_SALES_list=len(rule_list.filter(rule_type="SALES"))
    rule_ROYALTY_list=len(rule_list.filter(rule_type="ROYALTY"))
    rule_COGS_list=len(rule_list.filter(rule_type="COGS"))
    rule_MARGIN_list=len(rule_list.filter(rule_type="MARGIN"))

    sbd=Sales_breakdown_item.objects.all()
    sbd_contract=Sales_breakdown_per_contract.objects.filter(contract=contract)

    print(contract.status)
  #----------------------------------------------------------------------
  #---------------------IN_CREATION -------------------------------------
  #----------------------------------------------------------------------
    if contract.status=='IN_CREATION':
      return render(request, return_page, {
        # For Dashboard
          "contract":contract,
        # WRITER content:
          #main detail
            "contract_WRITER":contract,
            "milestone_list_WRITER":milestone_list,
            "attachement_list_WRITER":attachement_list,
            "sbd_WRITER":sbd,
            "sbd_contract_WRITER":sbd_contract,
            "rule_list_WRITER":rule_list,
            "rule_SALES_list_WRITER":rule_SALES_list,
            "rule_COGS_list_WRITER":rule_COGS_list,
            "rule_ROYALTY_list_WRITER":rule_ROYALTY_list,
            "rule_MARGIN_list_WRITER":rule_MARGIN_list,
            "tranche_list_WRITER":tranche_list,
            "contract_partner_list_WRITER":contract_partner_list,
          #specific to writer view
            "formulation_list":formulation_list,
            "region_list":region_list,
            "country_list":country_list,
            "partner_list":partner_list,
            "currency_list":currency_list,
            "periodicity_list":periodicity_list,
            "division_list":division_list,
            "brand_list":brand_list,
          #GOOGLE CAPTCHA
          'recaptcha_site_key':GOOGLE_RECAPTCHA_SITE_KEY
        })
  #---------------------------------------------------------------------- 
  #---------------------CURRENT-- -------------------------------------
  #----------------------------------------------------------------------
    if contract.status=='CURRENT':
      return render(request, return_page, {
        # For Dashboard
          "contract":contract,
        # WRITER content:
          #main detail
            "contract_WRITER":contract,
            "milestone_list_WRITER":milestone_list,
            "attachement_list_WRITER":attachement_list,
            "sbd_WRITER":sbd,
            "sbd_contract_WRITER":sbd_contract,
            "rule_list_WRITER":rule_list,
            "rule_SALES_list_WRITER":rule_SALES_list,
            "rule_COGS_list_WRITER":rule_COGS_list,
            "rule_ROYALTY_list_WRITER":rule_ROYALTY_list,
            "rule_MARGIN_list_WRITER":rule_MARGIN_list,
            "tranche_list_WRITER":tranche_list,
            "contract_partner_list_WRITER":contract_partner_list,
          #specific to writer view
            "formulation_list":formulation_list,
            "region_list":region_list,
            "country_list":country_list,
            "partner_list":partner_list,
            "currency_list":currency_list,
            "periodicity_list":periodicity_list,
            "division_list":division_list,
            "brand_list":brand_list,
        # VALIDATED content:
          #main detail
            "contract_VALIDATED":contract,
            "milestone_list_VALIDATED":milestone_list,
            "attachement_list_VALIDATED":attachement_list,
            #"sales_breakdown_list_VALIDATED":sales_breakdown_list,
            "sbd_VALIDATED":sbd,
            "sbd_contract_VALIDATED":sbd_contract,
            "rule_list_VALIDATED":rule_list,
            "rule_SALES_list_VALIDATED":rule_SALES_list,
            "rule_COGS_list_VALIDATED":rule_COGS_list,
            "rule_ROYALTY_list_VALIDATED":rule_ROYALTY_list,
            "rule_MARGIN_list_VALIDATED":rule_MARGIN_list,
            "tranche_list_VALIDATED":tranche_list,
            "contract_partner_list_VALIDATED":contract_partner_list,
          #GOOGLE CAPTCHA
          'recaptcha_site_key':GOOGLE_RECAPTCHA_SITE_KEY
        })
  #----------------------------------------------------------------------
  #---------------------DELETE/NEW- -------------------------------------
  #----------------------------------------------------------------------
    if contract.status in ['DELETE','NEW']:
      return render(request, return_page, {
        # For Dashboard
          "contract":contract,
        # PENDING_VALIDATION content:
          #main detail
            "contract_PENDING_VALIDATION":contract,
            "milestone_list_PENDING_VALIDATION":milestone_list,
            "attachement_list_PENDING_VALIDATION":attachement_list,
            "rule_list_PENDING_VALIDATION":rule_list,
            "rule_SALES_list_PENDING_VALIDATION":rule_SALES_list,
            "rule_COGS_list_PENDING_VALIDATION":rule_COGS_list,
            "rule_ROYALTY_list_PENDING_VALIDATION":rule_ROYALTY_list,
            "rule_MARGIN_list_PENDING_VALIDATION":rule_MARGIN_list,
            "tranche_list_PENDING_VALIDATION":tranche_list,
            "contract_partner_list_PENDING_VALIDATION":contract_partner_list,
            "sbd_PENDING_VALIDATION":sbd,
            "sbd_contract_PENDING_VALIDATION":sbd_contract,
          #GOOGLE CAPTCHA
          'recaptcha_site_key':GOOGLE_RECAPTCHA_SITE_KEY
        })
  #----------------------------------------------------------------------
  #---------------------CHANGE-------------------------------------------
  #----------------------------------------------------------------------
    if contract.status == 'CHANGE':
      # ---- get the value from the corresponding PROPOSAL 
      contract_proposal=contract.contract_proposal
      rule_list_PENDING_VALIDATION=Rule.objects.filter(contract=contract_proposal).select_related('qty_value_currency','tranche_currency')
      tranche_list_PENDING_VALIDATION=Tranche.objects.filter(rule__in=rule_list_PENDING_VALIDATION).order_by("id").select_related('rule')
      if contract_proposal.contract_type.name=="MARGIN_ADJ":
        for r in rule_list_PENDING_VALIDATION :
          if r.rule_type != "SALES":
            r.qty_value=abs(r.qty_value)
            r.rate_value=abs(r.rate_value)
        for t in tranche_list_PENDING_VALIDATION:
          t.percentage=abs(t.percentage) 
      sbd_contract_PENDING_VALIDATION=Sales_breakdown_per_contract.objects.filter(contract=contract_proposal)
      rule_SALES_list_PENDING_VALIDATION=len(rule_list_PENDING_VALIDATION.filter(rule_type="SALES"))
      rule_ROYALTY_list_PENDING_VALIDATION=len(rule_list_PENDING_VALIDATION.filter(rule_type="ROYALTY"))
      rule_COGS_list_PENDING_VALIDATION=len(rule_list_PENDING_VALIDATION.filter(rule_type="COGS"))
      rule_MARGIN_list_PENDING_VALIDATION=len(rule_list_PENDING_VALIDATION.filter(rule_type="MARGIN"))

      return render(request, return_page, {
        # For Dashboard
          "contract":contract,
        # PENDING_VALIDATION content:
          #main detail
            "contract_PENDING_VALIDATION":contract_proposal,
            "milestone_list_PENDING_VALIDATION":Milestone.objects.filter(contract=contract_proposal).select_related('currency'),
            "attachement_list_PENDING_VALIDATION":Contract_file.objects.filter(contract=contract_proposal),
            "rule_list_PENDING_VALIDATION":rule_list_PENDING_VALIDATION,
            "rule_SALES_list_PENDING_VALIDATION":rule_SALES_list_PENDING_VALIDATION,
            "rule_COGS_list_PENDING_VALIDATION":rule_COGS_list_PENDING_VALIDATION,
            "rule_ROYALTY_list_PENDING_VALIDATION":rule_ROYALTY_list_PENDING_VALIDATION,
            "rule_MARGIN_list_PENDING_VALIDATION":rule_MARGIN_list_PENDING_VALIDATION,
            "tranche_list_PENDING_VALIDATION":tranche_list_PENDING_VALIDATION,
            "contract_partner_list_PENDING_VALIDATION":Contract_partner.objects.filter(contract=contract_proposal),
            "sbd_PENDING_VALIDATION":sbd,
            "sbd_contract_PENDING_VALIDATION":sbd_contract_PENDING_VALIDATION,
        # VALIDATED content:
          #main detail
            "contract_VALIDATED":contract,
            "milestone_list_VALIDATED":milestone_list,
            "attachement_list_VALIDATED":attachement_list,
            "rule_list_VALIDATED":rule_list,
            "rule_SALES_list_VALIDATED":rule_SALES_list,
            "rule_COGS_list_VALIDATED":rule_COGS_list,
            "rule_ROYALTY_list_VALIDATED":rule_ROYALTY_list,
            "rule_MARGIN_list_VALIDATED":rule_MARGIN_list,
            "tranche_list_VALIDATED":tranche_list,
            "contract_partner_list_VALIDATED":contract_partner_list,
            "sbd_VALIDATED":sbd,
            "sbd_contract_VALIDATED":sbd_contract,
        })




@login_required(login_url='/login')
def invoices(request):
  contract_list=Contract.objects.filter(status__in=["CURRENT","CHANGE","DELETE",""]).order_by("contract_name").select_related('contract_currency','payment_periodicity')
  contract_partner_list=Contract_partner.objects.all().select_related('partner','contract')
  periodicity_cat_list=Periodicity_cat.objects.all().select_related('periodicity')
  invoice_list=Invoice.objects.all()
  country_list=Country.objects.all()
  currency_list=Currency.objects.all()
  return render(request, 'royalty_app/invoices.html', {"currency_list":currency_list,"country_list":country_list,"invoice_list":invoice_list,"periodicity_cat_list":periodicity_cat_list,"contract_partner_list":contract_partner_list,"contract_list":contract_list})

@login_required(login_url='/login')
def static_data(request):
  return render(request, 'royalty_app/static/static_data.html', {})

@login_required(login_url='/login')
def settings(request):
  return render(request, 'royalty_app/settings.html', {})

@login_required(login_url='/login')
def monthly_accruals(request):
  month_list=Month_table.objects.all()
  file_list=File.objects.filter(file_type="accruals")

  return render(request, 'royalty_app/reports/monthly_accruals.html', {"month_list":month_list,"file_list":file_list})

@login_required(login_url='/login')
def cash_flow_forecast(request):
  month_list=Month_table.objects.all()
  file_list=File.objects.filter(file_type="cash_forecast")
  current_month_nb=datetime.now().month
  return render(request, 'royalty_app/reports/cash_flow_forecast.html', {"current_month_nb":current_month_nb,"month_list":month_list,"file_list":file_list})

@login_required(login_url='/login')
def partner_report(request):
  month_list=Month_table.objects.all()
  file_list=File.objects.filter(file_type="partner_report")
  current_month_nb=datetime.now().month
  return render(request, 'royalty_app/reports/partner_report.html', {"current_month_nb":current_month_nb,"month_list":month_list,"file_list":file_list})



#------------------------------------------------------------------------
#                        API
#------------------------------------------------------------------------
#API Static Data

@login_required(login_url='/login')
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
  list_to_pd=Rule.objects.all().values_list('rule_type','id','contract_id','country_incl_excl','country_list','formulation','period_from','period_to','tranche_type','field_type','rate_value','qty_value')
  df_rule = pd.DataFrame.from_records(list(list_to_pd), columns=['rule_type','rule_id','contract_id','country_incl_excl','country_list','formulation','period_from','period_to','tranche_type','field_type','rate_value','qty_value'])
  
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
  list_to_pd=Accounting.objects.all().values_list('contract_type__name','transaction_direction','pl_bs','account_nb','cost_center_acc','market_acc','d_c_if_amount_positiv')
  df_accounting = pd.DataFrame.from_records(list(list_to_pd), columns=['contract type','transaction direction','PL or BS','account_nb','cost_center','market','D or C'])

  if df_accounting.empty:
    df_accounting=pd.DataFrame({'No Data': []})
  else:
    pass

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
    df_invoice=df_invoice[['contract_name','partner_name','amount','year','periodicity_cat','comment','booking_date','market_id','paid']]

  #Rule
  if df_rule.empty:
    df_rule=pd.DataFrame({'No Data': []})
  else:
    df_rule=pd.merge(df_rule,df_contract, how="inner",left_on=['contract_id'], right_on=['contract_id'] ) 
    df_rule=df_rule.rename(columns={'id_x':'rule_id'})
    df_rule=df_rule[['rule_id','contract_name','rule_type','country_incl_excl','country_list','formulation','period_from','period_to','tranche_type','field_type','rate_value','qty_value']]

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
        df_division.to_excel(writer, sheet_name='Division',index=False)

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
@login_required(login_url='/login')
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
@login_required(login_url='/login')
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
@login_required(login_url='/login')
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
        contract_type = Type.objects.get(id=data["type_id"]),
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
@login_required(login_url='/login')
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
@login_required(login_url='/login')
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

#------------------------------------------------------------------------------------------
#----------------------Modification/creation of a specific contract------------------------
#------------------------------------------------------------------------------------------

# API to save in database:


def response_validator(request):
  if request.method == "POST":
    contract_id=request.POST["contract_id"]
    response_validator = request.POST["reponse_validator"]
    contract = Contract.objects.get(id=contract_id)


    if response_validator in ["approve_contract_deletion","reject_contract_creation"]:
      contract.delete()
      return HttpResponseRedirect(reverse("contracts_to_validate"))

    if response_validator  in ["reject_contract_deletion","approve_contract_creation"]:
      contract.status="CURRENT"
      contract.save()
      return HttpResponseRedirect(reverse("contracts_to_validate"))

    if response_validator=="approve_contract_modification":
      #when modification is approved, 1) we delete the old contract, 2) we create a new_contract ( with ID same a the "old contract") 3) we copy from the proposal to new_contract 4) we delete the proposal
      contract_proposal_id=contract.contract_proposal.id

      #  loop though the Contract_file//Contract_partner//Rule//Tranche//Sales_breakdown_per_contract and delete
      Contract_file.objects.filter(contract=contract).delete()
      Contract_partner.objects.filter(contract=contract).delete()
      Milestone.objects.filter(contract=contract).delete()
      rule_list_old_contract=Rule.objects.filter(contract=contract)
      Tranche.objects.filter(rule__in=rule_list_old_contract).delete()
      Rule.objects.filter(contract=contract).delete()
      Sales_breakdown_per_contract.objects.filter(contract=contract).delete()
      
      # Copy contract summary from contract proposal
      new_contract=contract.contract_proposal
      new_contract.status="CURRENT"
      new_contract.pk=contract_id
      new_contract.save()
      

      # now loop though the Contract_file//Contract_partner//Tranche//Sales_breakdown_per_contract- with contract id =contract_proposal_id, and change it to contract_id
      # we copy the list of file_list currently used in the contract. after we have added the new file_contract , we will remove them 
      contract_proposal=Contract.objects.get(id=contract_proposal_id)
      contract_file_list=Contract_file.objects.filter(contract=contract_proposal)
      for cf in contract_file_list:
        cf.contract=new_contract
        cf.save()

      contract_partner_list=Contract_partner.objects.filter(contract=contract_proposal)
      for cp in contract_partner_list:
        cp.contract=new_contract 
        cp.save()

      milestone_list=Milestone.objects.filter(contract=contract_proposal)
      for milestone in milestone_list:
        milestone.contract=new_contract 
        milestone.save()

      rule_list=Rule.objects.filter(contract=contract_proposal)
      for r in rule_list:
        r.contract=new_contract 
        r.save()

      sales_breakdown_per_contract_list=Sales_breakdown_per_contract.objects.filter(contract=contract_proposal)
      for sb in sales_breakdown_per_contract_list:
        sb.contract=new_contract 
        sb.save()

      contract_proposal.delete()
      return HttpResponseRedirect(reverse("rules_current",args=[int(contract_id)]))

    if response_validator=="reject_contract_modification":
      print("response_validator")
      contract_proposal=contract.contract_proposal
      contract.status="CURRENT"
      contract.contract_proposal=None
      contract.save()
      contract_proposal.delete()
      return HttpResponseRedirect(reverse("rules_current",args=[int(contract_id)]))

  else:
    return HttpResponseRedirect(reverse("contracts_to_validate")) 

from django.core.files.base import ContentFile
@csrf_exempt 
@login_required(login_url='/login')
def pdf_file_to_keep(request,contract_id):
  user=request.user
  if user.role !="WRITER":
    return JsonResponse({"error": "as a non WRITER, you do not have the right to perform that task"}, status=201)
  else:
    try:
      data = json.loads(request.body)
      print(data)
      contract=Contract.objects.get(id=contract_id)
      if contract.status=="PROPOSAL": #then it means that we must copy the file from the corresponding CHANGE
        initial_contract=Contract.objects.get(contract_proposal=contract_id)
        contract_file_list=Contract_file.objects.filter(contract =initial_contract).filter (id__in =data["list"])
        for c in contract_file_list:
          new_file = ContentFile(c.upload.read())
          new_file.name = c.name
          contract_file_proposal = Contract_file(
            upload = new_file,
            contract = contract,
            name = c.name,
          )
          contract_file_proposal.save()
    except Exception as e:
      return JsonResponse({"error": f"data not loaded-   server message: {e}"}, status=404)

    if contract.status in ["IN_CREATION","NEW"]: 
      contract_file_list=Contract_file.objects.filter(contract =contract).exclude(id__in =data["list"])
      contract_file_list.delete()
    return JsonResponse({"response": "OK"}, status=201)


@csrf_exempt 
@login_required(login_url='/login')
def save_contract_basic_info(request,contract_id,save_type):
  user=request.user
  if user.role !="WRITER":
    return JsonResponse({"error": "as a non WRITER, you do not have the right to perform that task"}, status=201)
  else:
    contract=Contract.objects.get(id=contract_id)
    if contract.status not in ["IN_CREATION","CURRENT"] :
      return JsonResponse({"error": "an error occured"}, status=201)
    else:
      data = json.loads(request.body)
      if save_type=="SUBMIT_CHANGE" :
        contract_proposal=Contract(
          contract_type=Type.objects.get(id=data["contract_type"]),
          contract_name=data["contract_name"],
          transaction_direction=data["transaction_direction"],
          division=Division.objects.get(division_id=data["division_id"]),
          division_via=Division.objects.get(division_id=data["division_via_id"]),
          contract_currency=contract.contract_currency,
          payment_periodicity=contract.payment_periodicity,
          payment_terms=data["payment_terms"],
          m3_brand=Brand.objects.get(id=data["m3_brand"]),
          status="PROPOSAL"
        )
        contract_proposal.save()
        contract.contract_proposal=contract_proposal
        contract.status="CHANGE"
        contract.save()
        return JsonResponse({"contract_proposal_id": contract_proposal.id}, status=201)
      elif save_type=="SUBMIT_NEW":
        contract.status="NEW"

      contract.contract_name=data["contract_name"]
      contract.transaction_direction=data["transaction_direction"]
      contract.division=Division.objects.get(division_id=data["division_id"])
      contract.division_via=Division.objects.get(division_id=data["division_via_id"])
      contract.payment_terms=data["payment_terms"]
      contract.m3_brand=Brand.objects.get(id=data["m3_brand"])
      contract.save()
      return JsonResponse({"response": "OK"}, status=201)


@csrf_exempt 
@login_required(login_url='/login')
def save_contract_partner(request,contract_id):
  if request.method == "POST":
    user=request.user
    if user.role!="WRITER":
      return JsonResponse({"error": "as a non WRITER, you do not have the right to perform that task"}, status=201)
 
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
@login_required(login_url='/login')
def save_milestone(request,contract_id):
  if request.method == "POST":
    user=request.user
    if user.role!="WRITER":
      return JsonResponse({"error": "as a non WRITER, you do not have the right to perform that task"}, status=201)
    try: 
      contract=Contract.objects.get(id=contract_id)
      milestone_before_modification=Milestone.objects.filter(contract=contract)
      Milestone.objects.filter(contract=contract).delete()    #delete the existing record 
      data = json.loads(request.body)
      for item in data :
        booked=item['booked']
        if booked =="NO":
          booking_date="1900-01-01"
          payment_date="1900-01-01"
          market=Country.objects.get(country_id="USA")
        else:
          booking_date=item['booking_date']
          payment_date=item['payment_date']
          market=Country.objects.get(country_id=item['market'])

        m=Milestone(
          contract = contract,
          name=item['name'],
          amount=item['amount'],
          currency=Currency.objects.get(currency=item['currency']),
          booked=booked,
          market=market,
          booking_date=booking_date,
          payment_date=payment_date,
        )
        m.save()
    except Exception as e:
      for  m in milestone_before_modification:
        m.save()
      return JsonResponse({"error": f"data not loaded-   server message: {e}"}, status=404)
    return JsonResponse({"response": "OK"}, status=201)
  else:
    return JsonResponse({"error": "GET or PUT request required."}, status=400)


@csrf_exempt
@login_required(login_url='/login')
def save_rule(request,contract_id):

  if request.method == "POST":
    user=request.user
    if user.role!="WRITER":
      return JsonResponse({"error": "as a non WRITER, you do not have the right to perform that task"}, status=201)
 
    contract=Contract.objects.get(id=contract_id)
    rules_before_modification=Rule.objects.filter(contract=contract)
    Rule.objects.filter(contract=contract).delete()    #delete the existing record for this contract_partner ( we replace then, see code after:)
    data = json.loads(request.body)
    for item in data :
      try:  
        if item['tranche_currency']=="same_as_contract" :
          tranche_currency=contract.contract_currency
        else:
          tranche_currency=Currency.objects.get(currency=item['tranche_currency'])
        
        if (', '.join(item['country']))=='' :
          country_list='---'
        else:
          country_list=', '.join(item['country'])

        qty_value_currency=Currency.objects.get(currency=item['qty_value_currency'])
        

        r=Rule(
          contract = contract,
          rule_type=item['rule_type'],
          country_incl_excl=item['country_incl_excl'],
          field_type=item['field_type'],
          period_from=item['period_from'],
          period_to=item['period_to'],
          tranche_type=item['tranche_type'],
          rate_value=item['rate_value'],
          qty_value=item['qty_value'],
          qty_value_currency=qty_value_currency,
          tranche_currency=tranche_currency,
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

#API to save new mini gar
@csrf_exempt
@login_required(login_url='/login')
def save_mini(request,contract_id):
 
  try:
    contract = Contract.objects.get( id=contract_id)
  except contract.DoesNotExist:
    return JsonResponse({"error": "post not found."}, status=404)
  user=request.user
  if user.role!="WRITER":
    return JsonResponse({"error": "as a non WRITER, you do not have the right to perform that task"}, status=201)
 
  if request.method == "PUT":
    data = json.loads(request.body)

    if data["country_id"] == "" : 
      minimum_guar_remaining_allocation_country= None
    else :
      minimum_guar_remaining_allocation_country=Country.objects.get(country_id=data["country_id"])
    
    if data["amount"] == "" : 
      minimum_guar_amount= None
    else :
      minimum_guar_amount=data["amount"] 
    contract.mini_gar_status = data["mini_gar_status"]
    contract.mini_gar_from = data["mini_gar_from"]
    contract.mini_gar_to = data["mini_gar_to"]
    contract.minimum_guar_amount = minimum_guar_amount
    contract.minimum_guar_remaining_allocation_country=minimum_guar_remaining_allocation_country
    contract.save()
    return JsonResponse({"result": "all done"}, status=201)

  else:
    return JsonResponse({"error": "GET or PUT request required."}, status=400)

@csrf_exempt 
@login_required(login_url='/login')
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
@login_required(login_url='/login')
def new_invoice(request):
  if request.method == "POST":
    data = json.loads(request.body)

    try:  
      invoice=Invoice(
        contract = Contract.objects.get(id=data["contract_id"]),
        partner = Partner.objects.get(id=data["partner_id"]),
        amount=data["amount_value"],
        currency = Currency.objects.get(currency=data["currency"]),
        booking_date=data["booking_date"],
        year=data["year_value"],
        periodicity_cat= Periodicity_cat.objects.get(id=data["period_id"]),
        comment = data["comment_value"],
        market = Country.objects.get(country_id=data["market_id"]),
      )
      invoice.save()
      
      return JsonResponse({"invoice_id": invoice.id}, status=201)
    except Exception as e:
      return JsonResponse({"error": f"data not loaded-   server message: {e}"}, status=404)

@csrf_exempt
@login_required(login_url='/login')
def new_contract_file(request): 
  if request.method == "POST":
    user=request.user
    if user.role!="WRITER":
      return JsonResponse({"error": "as a non WRITER, you do not have the right to perform that task"}, status=201)
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
@login_required(login_url='/login')
def delete_row_invoice(request,invoice_id):
  user=request.user
  if user.role=="WRITER" :
    if request.method == "POST":
      invoice=Invoice.objects.get(pk=invoice_id)
      invoice.delete()
      return JsonResponse({"result": "all done"}, status=201)
    else:
      return JsonResponse({"error": "GET or PUT request required."}, status=400)
  return JsonResponse({"error": "only WRITER can make a modification"}, status=400)


@csrf_exempt
@login_required(login_url='/login')
def delete_row_file(request,file_id):
  user=request.user
  if user.role=="WRITER" :
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
  return JsonResponse({"error": "only WRITER can make a modification"}, status=400)
  
@csrf_exempt
@login_required(login_url='/login')
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
@login_required(login_url='/login')
def new_report(request):
  #return JsonResponse({"error": "postgresql+psycopg2://" }, status=400)

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
    #       f-Calculation Accounting_entry
    #   III: Save calculation in database

    #   I: book file name in database
  if request.method == "POST":

    #Import File
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

        #Contract
        contract_list=Contract.objects.filter(status__in=["CURRENT","DELETE","CHANGE"]) # we only select contracts that are valid
        df_contract = pd.DataFrame(list(contract_list.values()))
        if (df_contract.empty):
              file.delete()
              return JsonResponse({"error": "Please make sure that at least one contract is valid"}, status=201)   
        df_contract=df_contract.rename(columns={'id':'contract_id','contract_currency_id':'contract_currency','division_id':'division'})
        
        
        print(df_contract)
        print("contract")

        #Rule
        rule_list=Rule.objects.filter(contract__in=contract_list) # we only select the rules related to the authorised contract ( see above)
        rule_values_list=rule_list.values_list('id','contract_id','rule_type','country_incl_excl','country_list','formulation','period_from','period_to','tranche_type','field_type','rate_value','qty_value','tranche_currency','qty_value_currency')
        print("rule_list")
        df_rule = pd.DataFrame.from_records(list(rule_values_list), columns=['rule_id','contract_id','rule_type','country_incl_excl','country_list','formulation','period_from','period_to','tranche_type','field_type','rate_value','qty_value','tranche_currency','qty_value_currency'])
        
          #Each rule is composed on a beginning and end date. If the period goes across different years, we must break the row- i.e. 01/01/2019 to 10/10/2020 --> 01/01/2019 to 31/12/2019 // 01/01/2020 to 10/10/2020
        df_rule= df_year_nb_month.merge(df_rule, how="cross" ) #some contracts have a long period (i.e. 01/01/1990 to 01/01/2030), while the period under analysis only concernd a few years- do that reason, we utilise the "df_year_nb_month", which is the period chosen by the user for the analysis 
        filtered_values = np.where((pd.DatetimeIndex(df_rule['period_from']).year <= df_rule['year']) & (pd.DatetimeIndex(df_rule['period_to']).year >= df_rule['year']) ) 
        df_rule=df_rule.loc[filtered_values]
      
        df_rule['month']='1'
        df_rule['day']='1'
        df_rule['period_from']=np.where(
          pd.DatetimeIndex(df_rule['period_from']).year==df_rule['year'],
          pd.to_datetime(df_rule['period_from']), 
          pd.to_datetime(df_rule[['year', 'month','day']], errors = 'coerce')
        )

        df_rule['month']='12'
        df_rule['day']='31'
        df_rule['period_to']=np.where(
          pd.DatetimeIndex(df_rule['period_to']).year==df_rule['year'],
          pd.to_datetime(df_rule['period_to']), 
          pd.to_datetime(df_rule[['year', 'month','day']], errors = 'coerce')
        )
     
        df_rule['period_from']=pd.to_datetime(df_rule['period_from'],format='%d.%m.%Y')
        df_rule['period_to']=pd.to_datetime(df_rule['period_to'],format='%d.%m.%Y')

        df_rule=df_rule.drop(['month_nb','month','day'], axis = 1)

        if df_rule.empty: 
          df_rule=pd.DataFrame({
            'year': [0],
            'rule_id': [0],
            'contract_id': [0],
            'rule_type':[''],
            'country_incl_excl': [''],
            'country_list': ['0'],
            'formulation': ['0'],
            'period_from': ['1900-01-01'],
            'period_to': ['1900-01-01'],
            'tranche_type': [''],
            'field_type': [''],
            'sales_rate': [0],
            'qty_value': [0],
            'tranche_currency': [''],
            'qty_value_currency': [''],
          })
        print('df_rule')

   
        #Tranche
        tranche_list=Tranche.objects.filter(rule__in=rule_list) # we only select the tranches that are related to the rules previously selected
        df_tranche = pd.DataFrame(list(tranche_list.values()))
        filehandle = request.FILES.get("file")
        print("tranche")
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

        #Milestone
        milestone_list=Milestone.objects.filter(contract__in=contract_list).filter(booked="YES")

        df_milestone = pd.DataFrame(list(milestone_list.values()))
        df_milestone_empty=pd.DataFrame({
            'id': [0],
            'contract_id': [0],
            'name': [''],
            'amount': [0],
            'currency_id': [0],
            'booked': [''],
            'market_id': [0],
            'year': [0], #=year_booking
            'month': [0],#=month_booking
            'payment_date': [''],
          })
      
        if df_milestone.empty:
          df_milestone=df_milestone
        else:
          df_milestone['month_booking']=pd.DatetimeIndex(df_milestone['booking_date']).month # we filter the invoice booked during the period under analysis
          df_milestone['year_booking']=pd.DatetimeIndex(df_milestone['booking_date']).year
          df_milestone=pd.merge(df_milestone,df_year_month, how="inner",left_on=['year_booking','month_booking'], right_on=['year','month'] )
          df_milestone=df_milestone.drop(['year_booking','month_booking'], axis = 1)
          # if the invoices have been booked at a time not mentionned in the from/to period, the dataframe will be empty- same as mention before, we must fill in the table anyway
          if df_milestone.empty:
            df_milestone=df_milestone_empty
        print("milestone done")
        
        #Sales_breakdown_item
        
        sales_breakdown_item_list=Sales_breakdown_item.objects.all()
        df_sales_breakdown_item = pd.DataFrame(list(sales_breakdown_item_list.values()))
        if df_sales_breakdown_item.empty: 
          df_sales_breakdown_item=pd.DataFrame({
            'id': [0],
            'sales_breakdown_definition': ['NA'],
          })

        #Sales_breakdown_per_contract
        breakdown_per_contract_list=Sales_breakdown_per_contract.objects.filter(contract__in=contract_list)
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
        print("df_breakdown_per_contract")

    
        #Contract_partner
        contract_partner_list=Contract_partner.objects.filter(contract__in=contract_list)
        df_contract_partner = pd.DataFrame(list(contract_partner_list.values()))
        if df_contract_partner.empty:  
          df_contract_partner=pd.DataFrame({
            'contract_id': [0],
            'partner_id': [0],
            'percentage': [0],
          })

        #Invoice
        invoice_list=Invoice.objects.filter(contract__in=contract_list)
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
            'market_id': [''],
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

        print("definition of invoice: Done")

        #Sale
        df_sales = pd.read_excel(filehandle, 'Sales',dtype={'formulation':str,'year':int,'month':int})
        df_sales_empty=pd.DataFrame({
            'year': [0],
            'month': [0],
            'country_id': [''],
            'formulation': [''],
            'volume': [0],
            'sales': [0],
            'sales_currency': ['-'],
          })
        if not df_sales.empty:
          df_sales=pd.merge(df_sales,df_year_month, how="inner",left_on=['year','month'], right_on=['year','month'] )
          if not df_sales.empty:
            #check that all countries that are part of the sales file are in the df_country
            df_sales_country_list=df_sales.drop_duplicates(subset=['country_id'])
            df_sales_country_list=pd.merge(df_sales_country_list,df_country, how="left",left_on=['country_id'], right_on=['country_id'] ).fillna("NaN")
            df_sales_country_list=df_sales_country_list[df_sales_country_list.country =="NaN"][['country_id']]
            if not df_sales_country_list.empty:
              df_sales_country_list=df_sales_country_list.values.tolist()
              df_sales_country_list=','.join([y[0] for y in df_sales_country_list])

              file.delete()
              print(f"the following countrie(s) are missing in your static files: {df_sales_country_list}")
              return JsonResponse({"error": f"the following countrie(s) are missing in your static files: {df_sales_country_list}"}, status=201)              
        
        print("df_sales")

        #FX
        df_fx = pd.read_excel(filehandle, 'Fx',dtype={'year':int})
        df_fx = df_fx[[ 'year','currency','exchange_rate']]
 
        df_fx=pd.merge(df_fx,df_year_nb_month, how="inner",left_on=['year'], right_on=['year'] )
        df_fx=df_fx.drop(['month_nb'], axis = 1)
        if df_fx.empty:
          file.delete()
          return JsonResponse({"error": f"No Fx available for the period selected"}, status=201)
        
        #verify that , for each year/cur in df_file, there is a year/cur in FX file:
        df_sales_curr_list=df_sales.drop_duplicates(subset=['year','sales_currency'])
        df_fx_curr_list=df_fx.drop_duplicates(subset=['year','currency'])
        df_sales_curr_list=pd.merge(df_sales_curr_list,df_fx_curr_list, how="left",left_on=['year','sales_currency'], right_on=['year','currency'] ).fillna("NaN")

        df_sales_curr_list=df_sales_curr_list.loc[df_sales_curr_list.currency =="NaN"][['sales_currency','year']]  

        if not df_sales_curr_list.empty:
          df_sales_curr_list=df_sales_curr_list.values.tolist()
          df_sales_curr_list=','.join([f'{y[0]} {y[1]}' for y in df_sales_curr_list])
          file.delete()
          return JsonResponse({"error": f"the following currency-year pair are missing in your FX file: {df_sales_curr_list}"}, status=201)   

        print("df_fx")
        if df_sales.empty:
          df_sales=df_sales_empty
        print("df_sales done")


          # in the event the user load a data without the SKU and SKU_name ( for accruals and CCF), we should create the below columns
        if 'SKU' not in df_sales.head() :
          df_sales['SKU']=None
        if 'SKU_name' not in df_sales.head() :
          df_sales['SKU_name']=None
        df_sales['SKU']=df_sales['SKU'].astype(str)


        df_sales_breakdown=df_sales.copy()
        df_sales=df_sales[['year','month','country_id','formulation','SKU','SKU_name','sales_currency','volume','sales']]
        print("definition of df_sales: Done")


        #check that there is an FX for the QTY rule curr

        df_qty_currency=df_rule[df_rule.field_type=="QTY"]
        if not df_qty_currency.empty :
          df_qty_currency=df_qty_currency.drop_duplicates(subset=['year','qty_value_currency'])
          df_qty_currency=pd.merge(df_qty_currency,df_fx, how="left",left_on=['year','qty_value_currency'], right_on=['year','currency'] ).fillna("NaN")
          df_qty_currency=df_qty_currency[df_qty_currency.currency=="NaN"][['year','qty_value_currency']]
          if not df_qty_currency.empty :
            df_qty_currency=df_qty_currency.values.tolist()
            df_qty_currency=','.join([f'{y[0]} {y[1]}' for y in df_qty_currency])              
            file.delete()
            return JsonResponse({"error": f"the following currency-year pair are missing in your FX file: {df_qty_currency}"}, status=201)   

        #check that there is an FX for the tranche curr 

        df_tranche_currency=df_rule[df_rule.tranche_type=="YES"]
        if not df_tranche_currency.empty :
          df_tranche_currency=df_tranche_currency.drop_duplicates(subset=['year','tranche_currency'])
          df_tranche_currency=pd.merge(df_tranche_currency,df_fx, how="left",left_on=['year','tranche_currency'], right_on=['year','currency'] ).fillna("NaN")
          df_tranche_currency=df_tranche_currency[df_tranche_currency.currency=="NaN"][['year','tranche_currency']]
          if not df_tranche_currency.empty :
            df_tranche_currency=df_tranche_currency.values.tolist()
            df_tranche_currency=','.join([f'{y[0]} {y[1]}' for y in df_tranche_currency])              
            file.delete()
            return JsonResponse({"error": f"the following currency-year pair are missing in your FX file: {df_tranche_currency}"}, status=201)  

        #--------Calculate sales break_down so that the user can see the breakdown per contract----------
        #first, break the import
        if file.file_type=="partner_report" :
          print('df_sales_breakdown 0')

          df_sales_breakdown=pd.melt(
            df_sales_breakdown,
            id_vars=['year','month','country_id','formulation','SKU','SKU_name','sales_currency','volume'],
            var_name="sales_breakdown_definition",
            value_name="sales_in_market_curr",
          )
          print('df_sales_breakdown 1')

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
          print("df_sales_breakdown 2")

          df_sales_breakdown=pd.merge(df_rule,df_sales_breakdown, how="inner",left_on=['formulation','year'], right_on=['formulation','year'] )
          if not df_sales_breakdown.empty :
            df_sales_breakdown['country_validation']=(
                                        ((df_sales_breakdown.apply(lambda x: x.country_id in x.country_list, axis=1))& (df_sales_breakdown['country_incl_excl'] == "INCLUDE") ) | 
                                        ((df_sales_breakdown.apply(lambda x: x.country_id not in x.country_list, axis=1))& (df_sales_breakdown['country_incl_excl'] == "EXCLUDE") )
                                      )
            print("df_sales_breakdown 1")
            print(df_sales_breakdown)
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
            df_sales_breakdown=df_sales_breakdown[['contract_id','contract_name','year','month','country_id','formulation','SKU','SKU_name','sales_currency','volume','sales_in_market_curr','sales_in_contract_curr','sales_breakdown_definition','contract_currency']]

            #link to breakdown def:


            df_sales_breakdown=pd.merge(df_sales_breakdown,df_breakdown_per_contract, how="left",left_on=['contract_id','sales_breakdown_definition'], right_on=['contract_id_breakdown','sales_breakdown_definition'] )
            df_sales_breakdown=df_sales_breakdown[['contract_name','year','month','country_id','formulation','SKU','SKU_name','sales_currency','volume','sales_breakdown_definition','sales_breakdown_contract_definition','contract_currency','sales_in_market_curr','sales_in_contract_curr']]       
          else:
            return JsonResponse({"error": f"No sales data to display- please make sure you "}, status=201)
       
    
        #---------------------------------------
        
      #b- calculation of rate per country and formulation
      #         i.  : average rate for contract with tranche  

        if not df_tranche.empty : 
          t1= pd.merge(df_rule,df_contract, how="inner",left_on=['contract_id'], right_on=['contract_id'] )
          #t1 and Sale
          
          print('t1')


          t2=pd.merge(t1,df_sales, how="inner",left_on=['formulation','year'], right_on=['formulation' ,'year'])
          print('t2 beginning')

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
            
            t2=t2[['rule_id','contract_currency','sales','sales_currency','tranche_currency','year']]
            print("T2")

            #t2 and fx - get sales currency
            t3=pd.merge(t2,df_fx, how="inner",left_on=['year','sales_currency'], right_on=['year','currency'] )
            t3 = t3.rename(columns={'exchange_rate': 'exchange_rate_from'})
            t3=pd.merge(t3,df_fx, how="inner",left_on=['year','tranche_currency'], right_on=['year','currency'] )
            t3 = t3.rename(columns={'exchange_rate': 'exchange_rate_to'})
            # calculate sales amount in report currency
            t3['sales_in_report_curr']=t3['sales']*t3['exchange_rate_from']/t3['exchange_rate_to']
            
            t3=t3.fillna("")
            print("T3")

            t4=t3.groupby(['rule_id','year'], as_index=False).agg({"sales_in_report_curr": "sum"})
            #t5 - calculate amount sales and roy
            
            print("T4")



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
            t5['year']=t5['year'].fillna(0)

            print("T5")
            t6=t5.groupby(['rule_id','year'], as_index=False).agg({"roy": "sum","amount":"sum","mini_rate":"max"})
            t6['average_rate']=np.where(t6['amount']==0,
                                t6['mini_rate'],
                                t6['roy']/t6['amount']*100
                                ) 
            #-----------------link tranche average rate to general Rule -----------------

            print("t6")

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

        try:
          df_on_sales=pd.merge(df_rule_calc,df_sales, how="inner",left_on=['formulation','year'], right_on=['formulation','year'] )
          print('df_on_sales')

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
          df_on_sales=pd.merge(df_on_sales,df_fx, how="inner",left_on=['year','tranche_currency'], right_on=['year','currency'] )
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
          df_on_sales['amount_payment_curr']=df_on_sales['amount_contract_curr'] # payment for roy based on sales are made in contract currency
          df_on_sales['payment_currency_id']=df_on_sales['contract_currency']
          df_on_sales['payment_date']=None
          df_on_sales=df_on_sales[['contract_id','rule_type','year','month','SKU','SKU_name','amount_payment_curr','amount_contract_curr','payment_periodicity_id','market_id','sales_in_market_curr','sales_in_contract_curr','volume','market_curr','field_type','sales_rate','qty_value','payment_currency_id','tranche_currency','qty_value_currency','payment_date']]
          df_on_sales=df_on_sales.fillna("")

          print("def_on_sales 5")# // 
          df_on_sales=df_on_sales.groupby(['contract_id','rule_type','year','month','SKU','SKU_name','payment_periodicity_id','market_id','market_curr','field_type','sales_rate','qty_value','payment_currency_id','tranche_currency','qty_value_currency','payment_date'], as_index=False).agg({"amount_contract_curr": "sum","amount_payment_curr":"sum","sales_in_market_curr": "sum","sales_in_contract_curr": "sum","volume":"sum"})

          #df_on_sales['rule_type']='INVOICE'

          roy_on_sales_empty=df_on_sales.empty
        except:
          roy_on_sales_empty=df_on_sales.empty
          df_on_sales=pd.DataFrame({
          'contract_id': [0],
          'rule_type': [''],
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
          'payment_currency_id': [''],
          'tranche_currency': [''],
          'qty_value_currency': [0],
          'amount_contract_curr': [0],
          'amount_payment_curr': [0],
          'sales_in_market_curr': [0],
          'sales_in_contract_curr': [0],
          'volume': [0],
          'payment_date':'NA',
        })
        print(df_on_sales)
      #         ii. : Milestone
        if not df_milestone.empty :

          df_milestone=pd.merge(df_milestone,df_contract, how="inner",left_on=['contract_id'], right_on=['contract_id'] )
          print("Milestone 1")


          # convert the Milestone in contract currency
          df_milestone=pd.merge(df_milestone,df_fx, how="inner",left_on=['year','currency_id'], right_on=['year','currency'] )
          df_milestone = df_milestone.rename(columns={'exchange_rate': 'fx_from'})
          df_milestone=pd.merge(df_milestone,df_fx, how="inner",left_on=['year','contract_currency'], right_on=['year','currency'] )
          df_milestone = df_milestone.rename(columns={'exchange_rate': 'fx_to'})
          df_milestone = df_milestone.rename(columns={'country_id': 'market_id'})
          df_milestone = df_milestone.rename(columns={'currency_id': 'payment_currency_id'})
          df_milestone = df_milestone.rename(columns={'amount': 'amount_payment_curr'})
          print("Milestone 2")

          df_milestone["amount_contract_curr"]=df_milestone["amount_payment_curr"]*df_milestone["fx_from"]/df_milestone["fx_to"]
          df_milestone["market_curr"]=""
          df_milestone["rule_type"]="MILESTONE"
          df_milestone["sales_in_market_curr"]=0
          df_milestone["sales_in_contract_curr"]=0
          df_milestone["SKU"]=""
          df_milestone["SKU_name"]=""
          df_milestone["volume"]=0
          df_milestone["tranche_currency"]=""
          df_milestone["field_type"]=""
          df_milestone["sales_rate"]=0
          df_milestone["qty_value"]=0
          df_milestone["qty_value_currency"]=""

          df_milestone=df_milestone[['contract_id','rule_type','year','month','SKU','SKU_name','amount_contract_curr','amount_payment_curr','payment_currency_id','payment_periodicity_id','market_id','sales_in_market_curr','sales_in_contract_curr','volume','market_curr','field_type','sales_rate','qty_value','tranche_currency','qty_value_currency','payment_date']]
          df_milestone=df_milestone.groupby(['contract_id','rule_type','year','month','SKU','SKU_name','payment_periodicity_id','market_id','market_curr','field_type','sales_rate','qty_value','payment_currency_id','tranche_currency','qty_value_currency','payment_date'], as_index=False).agg({"amount_contract_curr": "sum","amount_payment_curr":"sum","sales_in_market_curr": "sum","sales_in_contract_curr":"sum","volume":"sum"})
          print("Milestone 3")
        
        milestone_empty=df_milestone.empty
        print(df_milestone)
      #         iii. : Mini Gar 

        print("Mini Gar2")

        #get contract with mini gar
        df_mini_gar=df_contract.copy()
        df_mini_gar['ismini']=(df_mini_gar['mini_gar_status']=='YES')
        df_mini_gar=df_mini_gar[df_mini_gar.ismini ==True]

        #in case there are no market_id ( as it is not necessary to allocate the amount on a specific market), 
        df_mini_gar= df_mini_gar.rename(columns={'minimum_guar_remaining_allocation_country_id':'market_id'})
        df_mini_gar['market_id']= df_mini_gar['market_id'].fillna("NA")
        print("Mini Gar3")

        #df_year_nb_month and df_mini_gar
        df_mini_gar=df_mini_gar.merge(df_year_nb_month,how='cross')        
        df_mini_gar=df_mini_gar.loc[(df_mini_gar.year>=df_mini_gar.mini_gar_from) & (df_mini_gar.year<=df_mini_gar.mini_gar_to)]

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
        df_mini_gar['amount_payment_curr']=df_mini_gar['amount_contract_curr'] # payment for roy based on sales are made in contract currency
        df_mini_gar['payment_currency_id']=df_mini_gar['contract_currency'] # payment for roy based on sales are made in contract currency
        df_mini_gar["month"]=12
        print("Mini Gar6")
        df_mini_gar["market_curr"]=""
        df_mini_gar["rule_type"]="MINIMUM_GARANTEE"
        df_mini_gar["sales_in_market_curr"]=0
        df_mini_gar["sales_in_contract_curr"]=0
        df_mini_gar["SKU"]=""
        df_mini_gar["SKU_name"]=""
        df_mini_gar["volume"]=0
        df_mini_gar["tranche_currency"]=""
        df_mini_gar["field_type"]=""
        df_mini_gar["sales_rate"]=0
        df_mini_gar["qty_value"]=0
        df_mini_gar["qty_value_currency"]=""
        df_mini_gar["payment_date"]=''
        df_mini_gar = df_mini_gar.rename(columns={'payment_periodicity_id_x':'payment_periodicity_id'})
        df_mini_gar=df_mini_gar[['contract_id','rule_type','year','month','SKU','SKU_name','amount_contract_curr','amount_payment_curr','payment_periodicity_id','market_id','sales_in_market_curr','sales_in_contract_curr','volume','market_curr','field_type','sales_rate','qty_value','payment_currency_id','tranche_currency','qty_value_currency','payment_date']]
        df_mini_gar=df_mini_gar.groupby(['contract_id','rule_type','year','month','SKU','SKU_name','payment_periodicity_id','market_id','market_curr','field_type','sales_rate','qty_value','payment_currency_id','tranche_currency','qty_value_currency','payment_date'], as_index=False).agg({"amount_contract_curr": "sum","amount_payment_curr":"sum","sales_in_market_curr": "sum","sales_in_contract_curr":"sum","volume":"sum"})

        print("Mini Gar7")
        mini_gar_empty=df_mini_gar.empty

      #         iii. : append mini gar and roy on sales and Milestone
      
        #df_mini_gar=df_mini_gar.fillna("")
        df_on_sales=df_on_sales.fillna("")
        df_append=df_mini_gar.append(df_on_sales)
        df_append=df_append.append(df_milestone)
        print(df_on_sales)
        print(df_milestone)
        print("df_append")

        #merge with payment structure 
        
        df_payment_structure=df_payment_structure.rename(columns={'sales_month_id': 'sales_month'})#.astype(str)
        df_payment_terms=pd.merge(df_periodicity_cat,df_payment_structure, how="inner",left_on=['id'], right_on=['periodicity_cat_id'] )
        df_append=pd.merge(df_append,df_payment_terms, how="inner",left_on=['payment_periodicity_id','month'], right_on=['periodicity_id','sales_month'] )  
        print("df_append2") 
        df_append=df_append[['contract_id','rule_type','year','month','SKU','SKU_name','amount_contract_curr','payment_currency_id','amount_payment_curr','market_id','sales_in_market_curr','sales_in_contract_curr','volume','market_curr','field_type','sales_rate','qty_value','tranche_currency','qty_value_currency','periodicity_cat_id','payment_date']]
        print("df_append3")
        #merge with contract_partner and calculate amount per partner
        df_append=pd.merge(df_append,df_contract_partner, how="left",left_on=['contract_id'], right_on=['contract_id'] )
        df_append['percentage']=df_append['percentage'].fillna(100) #If the user did not insert a partner, then we should populate those fields
        df_append['partner_id']=df_append['partner_id'].fillna(0)#If the user did not insert a partner, then we should populate those fields
        df_append["amount_contract_curr"]=df_append["amount_contract_curr"]*df_append["percentage"]/100
        df_append= df_append.rename(columns={'percentage':'beneficiary_percentage'})
        df_append=df_append[['contract_id','rule_type','year','month','SKU','SKU_name','amount_contract_curr','payment_currency_id','amount_payment_curr','market_id','sales_in_market_curr','sales_in_contract_curr','volume','market_curr','field_type','sales_rate','qty_value','tranche_currency','qty_value_currency','periodicity_cat_id','partner_id','beneficiary_percentage','payment_date']]
        df_append['invoice_detail']=""
        df_append['invoice_paid']=""

        print("df_append 4")


      #         iv.: Invoice  

        df_invoice=pd.merge(df_year_nb_month,df_invoice, how="inner",left_on=['year'], right_on=['year'] )
        if not df_invoice.empty:
          df_invoice['rule_type']='INVOICE'
          df_invoice['month']=0
          df_invoice['SKU']=""
          df_invoice['SKU_name']=""
          df_invoice['market_curr']=""
          df_invoice['field_type']=""
          df_invoice['sales_rate']=0
          df_invoice['sales_in_market_curr']=0
          df_invoice['sales_in_contract_curr']=0
          df_invoice['volume']=0
          df_invoice['qty_value']=0
          df_invoice['tranche_currency']=""
          df_invoice['qty_value_currency']=""
          df_invoice['beneficiary_percentage']=0
          df_invoice['payment_date']=''
          df_invoice=df_invoice.rename(columns={'amount': 'amount_payment_curr'})
          df_invoice['payment_currency_id']=df_invoice['currency_id']

          # convert the invoice in contract currency
          df_invoice=pd.merge(df_invoice,df_contract, how="inner",left_on=['contract_id'], right_on=['contract_id'] ) # get contract currency
          df_invoice=pd.merge(df_invoice,df_fx, how="inner",left_on=['year','payment_currency_id'], right_on=['year','currency'] )
          df_invoice = df_invoice.rename(columns={'exchange_rate': 'fx_from'})
          df_invoice=pd.merge(df_invoice,df_fx, how="inner",left_on=['year','contract_currency'], right_on=['year','currency'] )
          df_invoice = df_invoice.rename(columns={'exchange_rate': 'fx_to'})
          df_invoice['amount_contract_curr']=df_invoice['amount_payment_curr']*df_invoice['fx_from']/df_invoice['fx_to']
          df_invoice=df_invoice.rename(columns={'comment': 'invoice_detail','paid':'invoice_paid'})
          df_invoice=df_invoice[['contract_id','rule_type','year','month','SKU','SKU_name','amount_contract_curr','payment_currency_id','amount_payment_curr','market_id','sales_in_market_curr','sales_in_contract_curr','volume','market_curr','field_type','sales_rate','qty_value','tranche_currency','qty_value_currency','periodicity_cat_id','partner_id','beneficiary_percentage','invoice_detail','invoice_paid']]
        invoice_empty=df_invoice.empty
        print("df_invoice: Done")
        #--------------------------------------------

        

      #         iv.: Detail : 

        print('df_append')
        
        if mini_gar_empty and roy_on_sales_empty and invoice_empty and milestone_empty:
          print("df_detail null")
          df_detail=pd.DataFrame({
            'division': [''],
            'division_country_id': [''],
            'division_via': [''],
            'field_type': [''],
            'year_of_sales': [0],
            'month_of_sales': [0],
            'SKU': [''],
            'SKU_name': [''],
            'market_id': [0],
            'sales_in_market_curr': [0],
            'sales_in_contract_curr': [0],
            'volume': [0],
            'market_curr': [''],
            'sales_rate': [0],
            'qty_value': [''],
            'beneficiary_percentage': [0],
            'amount_contract_curr': [0],
            'amount_payment_curr': [0],
            'contract_currency': [''],
            'transaction_direction': [''],
            'payment_currency_id': [''],
            'consolidation_currency': [''],
            'amount_consolidation_curr': [0],
            'contract_id': [0],
            'contract_name': [''],
            'contract_type_id': [0],
            'rule_type': [''],
            'partner_id': [0],
            'ico_3rd': [''],
            'partner_name': [''],
            'partner_country_id': [''],
            'brand_name': [''],
            'brand_code': [''],
            'period': [''],
            'invoice_paid': [''],
            'invoice_detail': [''],
            'payment_date': [''],
          })
        else:

          df_append=df_append.fillna("")
          df_invoice=df_invoice.fillna("") 
          df_detail=df_append.append(df_invoice)

          print("df_detail 00")


          # get last month of the period (i.e. for Q1, it's march)
          df_detail=pd.merge(df_detail,df_periodicity_cat, how="inner",left_on=['periodicity_cat_id'], right_on=['id'] )
          df_detail["day"]="1"
          df_detail = df_detail.rename(columns={"month":"month_of_sales","period_month_end_id":"period_month_end"})
          df_detail["month"]=df_detail["period_month_end"].astype(str)
          
          print("df_detail 01")

          df_detail["date"]= pd.to_datetime(df_detail[['year', 'month','day']], errors = 'coerce')
          df_detail["day_end_period"]= pd.to_datetime(df_detail['date'], format="%Y%m") + MonthEnd(1)
          df_detail=df_detail[['contract_id','rule_type','year','SKU','SKU_name','month_of_sales','amount_contract_curr','payment_currency_id','amount_payment_curr','periodicity_cat','market_id','sales_in_market_curr','sales_in_contract_curr','volume','market_curr','field_type','sales_rate','qty_value','tranche_currency','qty_value_currency','partner_id','beneficiary_percentage','invoice_detail','day_end_period','invoice_paid','payment_date']]
  
          print("df_detail 1")

          # get contract detail, get the payment terms and calculate the payment date 
          df_detail=pd.merge(df_detail,df_contract, how="inner",left_on=['contract_id'], right_on=['contract_id'] )
          
          '''
          df_detail["payment_date"]=df_detail["day_end_period"]+  pd.to_timedelta(df_detail['payment_terms'], unit='d')
          df_detail["payment_date"]= pd.to_datetime(df_detail['payment_date'],format='%d.%m.%Y') #needed, otherwise cannot load in system
          df_detail["payment_date"]=df_detail["payment_date"].astype(str)
          print(df_detail[["payment_date"]].dtypes)
          '''
          # In general, the payment will be automatically calculated based- but for Milestone, it should not ( as we already gide a payment date)
          df_detail["payment_date"]=pd.to_datetime(df_detail["payment_date"])
          df_detail["payment_date"]=df_detail["payment_date"].astype(str)
          df_detail["payment_date_calc"]=df_detail["day_end_period"]+  pd.to_timedelta(df_detail['payment_terms'], unit='d')
          df_detail["payment_date_calc"]= pd.to_datetime(df_detail['payment_date_calc'],format='%d.%m.%Y')
          df_detail["payment_date_calc"]=df_detail["payment_date_calc"].astype(str)

          df_detail["payment_date"]= np.where(
            df_detail["payment_date"] == "NaT",
            df_detail["payment_date_calc"],
            df_detail["payment_date"],
          )

          
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
          df_detail=df_detail[['division','division_country_id','division_via_id','field_type','year','month_of_sales','SKU','SKU_name','market_id','sales_in_market_curr','sales_in_contract_curr','volume','market_curr','sales_rate','qty_value','beneficiary_percentage','contract_currency','transaction_direction','amount_contract_curr','payment_currency_id','amount_payment_curr','consolidation_currency','amount_consolidation_curr','contract_id','contract_name','contract_type_id','rule_type','partner_id','ico_3rd','partner_name','partner_country_id','brand_name','brand_code','periodicity_cat','invoice_paid','invoice_detail','payment_date']]
          df_detail = df_detail.rename(columns={'division_via_id': 'division_via',"periodicity_cat":"period","year":"year_of_sales"})


          df_detail["invoice_paid"]=df_detail["invoice_paid"].astype(str)
          print(df_detail['payment_currency_id'].dtypes)

        print("definition of Detail: Done")

        

        #Tax impact--------------------- 
        if file.file_type=="cash_forecast": 
          df_wht=  df_detail.copy()
          df_wht['rule_type']=(df_wht['rule_type']=="INVOICE")
          df_wht=df_wht[df_wht.rule_type ==False]
          df_wht=df_wht.fillna("")
          df_wht=df_wht.groupby(['division','division_country_id','partner_country_id','ico_3rd','partner_name','payment_currency_id','transaction_direction'], as_index=False).agg({"amount_payment_curr": "sum"})    

          
          df_wht["country_from"]=np.where(
                                  df_wht["transaction_direction"]=="PAY",
                                  np.where(
                                    df_wht["amount_payment_curr"]>0,
                                    df_wht["division_country_id"],
                                    df_wht["partner_country_id"],
                                  ),
                                  np.where(
                                    df_wht["amount_payment_curr"]>0,
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
                                    df_wht["amount_payment_curr"]>0,
                                    "ICO-" + df_wht["division"] + " (" + df_wht["division_country_id"] + ")",
                                    np.where(
                                      df_wht["ico_3rd"]=="ICO",
                                      "ICO-" + df_wht["partner_name"] + "(" + df_wht["partner_country_id"]+ ")",
                                      "3rd " + "(" + df_wht["partner_country_id"]+ ")"
                                    )  
                                  ),
                                  np.where(
                                    df_wht["amount_payment_curr"]>0,
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
          df_wht['amount_payment_curr']=abs(df_wht['amount_payment_curr'])

          df_wht=df_wht.fillna("")
          df_wht=df_wht.groupby(['country_from','country_to','from_payor','to_payee','payment_currency_id'], as_index=False).agg({"amount_payment_curr": "sum"})

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

          df_wht=df_wht[['from_payor','to_payee','payment_currency_id','amount_payment_curr','wht_rate']]
          print("WHT Done")
          #         iv.:  summary cash flow--------------------- 
          # if REC, them - + if invoice -
          df_cash_flow= df_detail.copy()
          df_cash_flow=df_cash_flow.fillna("")
          df_cash_flow=df_cash_flow.groupby(['division','payment_currency_id','payment_date','rule_type','invoice_paid','transaction_direction'], as_index=False).agg({"amount_payment_curr": "sum"})

        if file.file_type=="accruals":
          #          v.:  Conso for accruals--------------------- 
          if mini_gar_empty and roy_on_sales_empty :

            df_conso=pd.DataFrame({
              'year_of_sales': [0],
              'division': [''],
              'brand_name': [''],
              'country': [''],
              'consolidation_currency': [''],
              'amount_consolidation_curr': [0],
            })
          else:
            df_conso= df_detail.copy()
            df_conso['rule_type']=(df_conso['rule_type']=="INVOICE")
            df_conso=df_conso[df_conso.rule_type ==False]
            df_conso["amount_consolidation_curr"]=np.where(df_conso["transaction_direction"]=="REC",-df_conso["amount_consolidation_curr"],df_conso["amount_consolidation_curr"])
            # import country name for market
            df_conso=pd.merge(df_conso,df_country, how="left",left_on=['market_id'], right_on=['country_id'] )
            #only keep columns
            df_conso=df_conso[['year_of_sales','division','brand_name','country','consolidation_currency','amount_consolidation_curr']]

            #sum and group
            df_conso=df_conso.fillna("")
            df_conso=df_conso.groupby(['year_of_sales','division','brand_name','country','consolidation_currency'], as_index=False).sum()     

          print("df_conso")  
          #          v.:  Accounting_entry for accruals---------------------
          if mini_gar_empty and roy_on_sales_empty and invoice_empty :
            df_accounting_entry=pd.DataFrame({
              'sheet_name': [''],
              'contract_type_id': [0],
              'division': [''],
              'contract_currency': [''],
              'accountingdate': [''],
              'reverseDate': [''],
              'account_nb': [''],
              'cost_center_acc': [''],
              'brand_code': [''],
              'market_acc': [''],
              'accruals_contract_curr': [0],
              'd_c': [''],
              'text_voucherline': [''],
            })
          else:
            df_accounting_entry= df_detail.copy()
            df_accounting_entry["accruals_contract_curr"]=np.where(df_accounting_entry["rule_type"]=="INVOICE",-df_accounting_entry["amount_contract_curr"],df_accounting_entry["amount_contract_curr"])
            
            df_accounting_entry=df_accounting_entry[['market_id','division','contract_type_id','brand_code','brand_name','transaction_direction','contract_currency','accruals_contract_curr']]
            df_accounting_entry=df_accounting_entry.fillna("")
            print("df_accounting_entry")
            print(df_accounting_entry)
            print("df_accounting")
            print(df_accounting)
            df_accounting_entry=pd.merge(df_accounting_entry,df_accounting, how="inner",left_on=['transaction_direction','contract_type_id'], right_on=['transaction_direction','contract_type_id'] )
            df_accounting_entry["market_acc"]=np.where(df_accounting_entry["market_acc"]=="SPLIT",df_accounting_entry["market_id"],df_accounting_entry["market_acc"])

            df_accounting_entry=df_accounting_entry.groupby(['division','contract_type_id','brand_code','brand_name','transaction_direction','contract_currency','account_nb','cost_center_acc','market_acc','pl_bs','d_c_if_amount_positiv'], as_index=False).agg({"accruals_contract_curr": "sum"})
            
            df_accounting_entry["brand_code"]=np.where(df_accounting_entry["pl_bs"]=="PL",df_accounting_entry["brand_code"],"")
            df_accounting_entry["d_c_if_amount_negativ"]=np.where(df_accounting_entry["d_c_if_amount_positiv"]=="C","D","C")
            df_accounting_entry["d_c"]=np.where(df_accounting_entry["accruals_contract_curr"]>0,df_accounting_entry["d_c_if_amount_positiv"],df_accounting_entry["d_c_if_amount_negativ"])
            df_accounting_entry["accruals_contract_curr"]=abs(df_accounting_entry["accruals_contract_curr"])

            df_accounting_entry=df_accounting_entry.round({'accruals_contract_curr': 0})
            df_accounting_entry["text_voucherline"]= 'ACCR. '+ df_accounting_entry["brand_name"]
            #Get Date
            df_accounting_entry["year"]=file.acc_year
            df_accounting_entry["month"]=file.acc_month.month_nb
            df_accounting_entry["day"]="1" 
            df_accounting_entry["date"]= pd.to_datetime(df_accounting_entry[['year', 'month','day']], errors = 'coerce')
            df_accounting_entry["accountingdate"]= pd.to_datetime(df_accounting_entry['date'], format="%Y%m") + MonthEnd(1)
            df_accounting_entry["reverseDate"]= df_accounting_entry["accountingdate"]+ timedelta(days=1)
            df_accounting_entry["accountingdate"]= df_accounting_entry["accountingdate"].dt.strftime('%d.%m.%Y')
            df_accounting_entry["reverseDate"]= df_accounting_entry["reverseDate"].dt.strftime('%d.%m.%Y')
            
            df_accounting_entry["sheet_name"]= "Accounting_" +df_accounting_entry["division"]+"_"+df_accounting_entry["contract_currency"]
            df_accounting_entry=df_accounting_entry.sort_values(['sheet_name','pl_bs','brand_name'], ascending=[1,0,1])
            df_accounting_entry=df_accounting_entry[['sheet_name','contract_type_id','division','contract_currency','accountingdate','reverseDate','account_nb','cost_center_acc','brand_code','market_acc','accruals_contract_curr','d_c','text_voucherline']]
          print("df_accounting_entry")

   

        #---------------Save in database----------------
        '''    
        conn = sqlite3.connect('royalty/db.sqlite3')
        '''
        
        final_db_url = f"postgresql+psycopg2://{DATABASE_URL_VIEW}"
        conn = create_engine(final_db_url)
        
        #-----------------------------------------------

        df_sales['import_file_id']=file.id
        df_sales.to_sql('royalty_app_sale', con=conn,index=False,if_exists="append")
        print("df_sales loaded succesfully")
        
        df_fx['import_file_id']=file.id
        df_fx.to_sql('royalty_app_fx', con=conn,index=False,if_exists="append")
        print("df_fx loaded succesfully")


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
        df_rule_calc=df_rule_calc[['contract_id','year','contract_name','country_incl_excl','country_list','period_from','period_to','formulation','tranche_type','field_type','qty_value','sales_rate']]
        df_rule_calc['import_file_id']=file.id
        df_rule_calc.to_sql('royalty_app_rule_calc', con=conn, index=False, if_exists="append")
        print("df_rule_calc loaded succesfully")

        df_detail['import_file_id']=file.id

        df_detail.to_sql('royalty_app_detail', con=conn, index=False, if_exists="append")
        print("df_detail loaded succesfully")
    
        if file.file_type=="cash_forecast":
          print(df_cash_flow)
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

          df_accounting_entry['import_file_id']=file.id
          df_accounting_entry.to_sql('royalty_app_accounting_entry', con=conn, index=False, if_exists="append")
          print("df_accounting_entry loaded succesfully")
        elif file.file_type=="partner_report":
          df_sales_breakdown['import_file_id']=file.id
          df_sales_breakdown.to_sql('royalty_app_sales_breakdown_for_contract_report', con=conn, index=False, if_exists="append") 
          print("df_sales_breakdown loaded succesfully")
      except Exception as e:
        file.delete()
        return JsonResponse({"error": f"something went wrong with the import file- please check that the format is respected-   server message: {e}"}, status=201)
      return JsonResponse({"file_id": file.id,"date":file.date}, status=201)
    except Exception as e:
      file.delete()
      return JsonResponse({"error": f"something went wrong with the import file- please check that the format is respected-   server message: {e}"}, status=201)

@login_required(login_url='/login')
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
        print(pd.DataFrame(list(detail_list.values())))
        df_detail_list = pd.DataFrame(list(detail_list.values())).drop(['id'], axis = 1)
        #name of type
        type_list=Type.objects.all()
        df_type=pd.DataFrame(list(type_list.values()))
        df_detail_list=pd.merge(df_type,df_detail_list,how="left",left_on=["id"],right_on=["contract_type_id"])
        df_detail_list=df_detail_list.drop(['contract_type_id','id'], axis = 1)
        df_detail_list=df_detail_list.rename(columns={'name':'contract_type'})
        
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

      if table_name=="accounting_entry":
        accounting_entry_list=Accounting_entry.objects.filter(import_file__in=file_object_list)
        df_accounting_entry = pd.DataFrame(list(accounting_entry_list.values())).drop(['id'], axis = 1)
        #add contract_type name
        type_list=Type.objects.all()
        df_type=pd.DataFrame(list(type_list.values()))
        df_accounting_entry=pd.merge(df_type,df_accounting_entry,how="left",left_on=["id"],right_on=["contract_type_id"])
        df_accounting_entry=df_accounting_entry.drop(['contract_type_id','id'], axis = 1)
        df_accounting_entry=df_accounting_entry.rename(columns={'name':'contract_type'})



        df_accounting_entry.to_excel(writer, sheet_name='Accounting',index=False)

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
    return render(request, 'royalty_app/static/division.html',  { "country_list":country_list ,"division_list":division_list})

  if table_name=="country":
    country_list=Country.objects.all().order_by("country_region","country_id").select_related('country_region')
    region_list=Region.objects.all()
    return render(request, 'royalty_app/static/country.html',  { "country_list":country_list ,"region_list":region_list})

  if table_name=="region":
    region_list=Region.objects.all()
    return render(request, 'royalty_app/static/region.html',  { "region_list":region_list})

  if table_name=="brand":
    brand_list=Brand.objects.all()
    return render(request, 'royalty_app/static/brand.html',  { "brand_list":brand_list})

  if table_name=="formulation":
    formulation_list=Formulation.objects.all()
    return render(request, 'royalty_app/static/formulation.html',  { "formulation_list":formulation_list})

  if table_name=="currency":
    currency_list=Currency.objects.all()
    return render(request, 'royalty_app/static/currency.html',  { "currency_list":currency_list})

  if table_name=="consolidation_currency":
    currency_list=Currency.objects.all()
    consolidation_currency=Consolidation_currency.objects.all().first()
    return render(request, 'royalty_app/static/consolidation_currency.html',  { "consolidation_currency":consolidation_currency,"currency_list":currency_list})

  if table_name=="accounting":
    accounting_list=Accounting.objects.all().select_related('contract_type')

    contract_type_list = Type.objects.all()
    country_list = Country.objects.all()
    country_list=list(country_list.values_list("country_id"))
    country_list=[ d[0] for d in country_list]
    market_list=['','SPLIT']+ country_list

    return render(request, 'royalty_app/static/accounting.html',  { "market_list":market_list,"contract_type_list":contract_type_list,"accounting_list":accounting_list})

  if table_name=="tax":
    tax_list=Tax.objects.all().select_related('country_from','country_to')
    country_list=Country.objects.all()
    return render(request, 'royalty_app/static/tax.html',  { "country_list":country_list,"tax_list":tax_list})

  if table_name=="sales_breakdown_item":
    sales_breakdown_item_list=Sales_breakdown_item.objects.all()
    return render(request, 'royalty_app/static/sales_breakdown_item.html',  { "sales_breakdown_item_list":sales_breakdown_item_list})

  if table_name=="payment_type":
    payment_type_list=Payment_type.objects.all()
    return render(request, 'royalty_app/static/payment_type.html',  { "payment_type_list":payment_type_list})





@csrf_exempt
@login_required(login_url='/login')
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
@login_required(login_url='/login')
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
@login_required(login_url='/login')
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
@login_required(login_url='/login')
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
        brand_code=d["brand_code"]
        brand_name=d["brand_name"]
        
        #if the item already exist, we modify it
        existing_items_equal_d=Brand.objects.filter(id=brand_id)
        if len(existing_items_equal_d)==1:  
          item_to_modify= existing_items_equal_d[0] 
          item_to_modify.brand_code=brand_code
          item_to_modify.brand_name=brand_name
          item_to_modify.save()
        #if the item is new, we create it
        else:
          mew_item=Brand(
            brand_code =brand_code,
            brand_name =brand_name,
          )
          mew_item.save()
      return JsonResponse({"success": "data loaded"}, status=201)
    except Exception as e:
      return JsonResponse({"error": f"data not loaded-   server message: {e}"}, status=404)


@csrf_exempt
@login_required(login_url='/login')
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
@login_required(login_url='/login')
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
@login_required(login_url='/login')
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
@login_required(login_url='/login')
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
@login_required(login_url='/login')
def save_accounting(request):
  if request.method == "POST":
    #Save File
    try:
      data = json.loads(request.body)

      for d in data :
        accounting_id=d["accounting_id"]
        item_to_modify=Accounting.objects.get(id=accounting_id)

        item_to_modify.contract_type=Type.objects.get(id=d["contract_type_id"])
        item_to_modify.transaction_direction=d["transaction_direction"]
        item_to_modify.account_nb=account_nb=d["account_nb"]
        item_to_modify.cost_center_acc=cost_center_acc=d["cost_center_acc"]
        item_to_modify.market_acc=market_acc=d["market_acc"]
        item_to_modify.pl_bs=pl_bs=d["pl_bs"]
        item_to_modify.d_c_if_amount_positiv=d["d_c_if_amount_positiv"]
        
        item_to_modify.save()

      return JsonResponse({"success": "data loaded"}, status=201)
    except Exception as e:
      return JsonResponse({"error": f"data not loaded-   server message: {e}"}, status=404)

@csrf_exempt
@login_required(login_url='/login')
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
@login_required(login_url='/login')
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



      