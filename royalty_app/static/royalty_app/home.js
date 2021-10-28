
function accruals_change(){
    //spinner activated

    spinner_on()

    myChart.reset()
    //make sure we are not missing any field
    year=document.getElementById("item_list_year").value
    contract_list=document.getElementById("item_list_contract").value
    contract_list=contract_list.split(", ")
    contract_type_list=document.getElementById("item_list_type_accruals").value
    contract_type_list=contract_type_list.split(", ")

    // We load it via a fetch in the API
    fetch(`/accruals_change`, {
        method: 'POST',
        body: JSON.stringify({
            year : year,
            contract_list:contract_list,
            contract_type_list:contract_type_list     
            }),
            
        })
        .then(response => response.json())
        .then(result => {
            if (!!result.error) {
                alert(result.error);
                location.reload();
            }else{
                data_roy_ytd_last_year=result.data_roy_ytd_last_year
                data_roy_ytd=result.data_roy_ytd
                data_accruals_last_year=result.data_accruals_last_year
                data_accruals=result.data_accruals
                for (var i = 0; i < 12; i++) {
                    myChart.data.datasets[3].data[i]=data_roy_ytd_last_year[i]
                    myChart.data.datasets[2].data[i]=data_roy_ytd[i]
                    myChart.data.datasets[1].data[i]=data_accruals_last_year[i]
                    myChart.data.datasets[0].data[i]=data_accruals[i]
                }
                myChart.update();
                spinner_off()
            }
        })
}
function cash_forecast_change(){
    //spinner activated

    spinner_on()

    myChart2.reset()
    pie_contract.reset()
    pie_country.reset()
    pie_currency.reset()
    //make sure we are not missing any field
    year=document.getElementById("item_list_year_forecast").value
    currency_list=document.getElementById("item_list_currency").value
    contract_list=document.getElementById("item_list_CFF_contract").value
    contract_list=contract_list.split(", ")
    contract_type_list=document.getElementById("item_list_type_cashflow").value


    currency_list=currency_list.split(", ")
    contract_type_list=contract_type_list.split(", ")

    // We load it via a fetch in the API
    fetch(`/cash_forecast_change`, {
        method: 'POST',
        body: JSON.stringify({
            year : year,
            currency_list:currency_list, 
            contract_type_list:contract_type_list,
            CFF_contract_id_list:contract_list   
            }),
        })
        .then(response => response.json())
        .then(result => {
            if (!!result.error) {
                alert(result.error);
                location.reload();
            }else{
                
                //update bar chart
                data_cash_forecast_last_year=result.data_cash_forecast_last_year
                data_cash_forecast=result.data_cash_forecast
  
                for (var i = 0; i < 12; i++) {
                    myChart2.data.datasets[1].data[i]=data_cash_forecast_last_year[i]
                    myChart2.data.datasets[0].data[i]=data_cash_forecast[i]
                }
                myChart2.update();

                //update pie chart contract
                pie_contract.data.datasets[0].data=result.data_contract
                pie_contract.data.datasets[0].backgroundColor=result.color_contract
                pie_contract.data.labels=result.labels_contract
                pie_contract.update();

                //update pie chart contract
                pie_country.data.datasets[0].data=result.data_country
                pie_country.data.datasets[0].backgroundColor=result.color_country
                pie_country.data.labels=result.labels_country
                pie_country.update();

                //update pie chart currency
                pie_currency.data.datasets[0].data=result.data_currency
                pie_currency.data.datasets[0].backgroundColor=result.color_currency
                pie_currency.data.labels=result.labels_currency
                pie_currency.update();

                //total amount:
                document.getElementById("total_amount").innerHTML=result.total_amount
                //spinner desactivated
                spinner_off()
            }
        })
}

function selectall(elm,report_change){
    comboTreeWrapper=get_comboTreeWrapper_list(elm)
    var checked_box_list=comboTreeWrapper.querySelectorAll('input[type=checkbox]') 
    var select_mode=elm.textContent 
    var select_all_box= comboTreeWrapper.querySelector(".justAnInputBox")
    var comboTreeHiddenBox=comboTreeWrapper.querySelector(".comboTreeHiddenBox")
    select_all_box.style.color=null

    if (select_mode=="(select all)"){
        elm.textContent="(unselect all)"
        checked_status=true
        select_all_box.innerHTML="All"
    }else{
        elm.textContent="(select all)"
        checked_status=false
        select_all_box.innerHTML="Select"
        select_all_box.style.color="grey"
    }    
    item_code_list=[]   
    //go throug list and selec or unselect all check box
    for (i = 0; i < checked_box_list.length; ++i) {
        checked_box_list[i].checked=checked_status
        item_code_list.push(checked_box_list[i].getAttribute("item_code"))
        }
  
    if (checked_status== false)
        item_code_list=[]
        
    //item_list_display_form_new_hidden.value=imput_list
    comboTreeHiddenBox.value=item_code_list.join(', ')

    if (report_change== "accruals_change"){
        accruals_change()
    }else if (report_change== "cash_forecast_change"){
        cash_forecast_change()
    }

}

