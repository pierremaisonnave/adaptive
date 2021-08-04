
function accruals_change(elm){
    //spinner activated
    spinner=document.getElementById("spinner_load_page")
    spinner.style.display = "block"

    myChart.reset()
    //make sure we are not missing any field
    year=document.getElementById("item_list_year").value
    contract_list=document.getElementById("item_list_contract").value
    contract_list=contract_list.split(",")
    // We load it via a fetch in the API
    fetch(`/accruals_change`, {
        method: 'POST',
        body: JSON.stringify({
            year : year,
            contract_list:contract_list      
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
                spinner.style.display = "none"
            }
        })
}
function cash_forecast_change(){
    //spinner activated
    spinner=document.getElementById("spinner_load_page")
    spinner.style.display = "block"

    myChart2.reset()
    pie_contract.reset()
    pie_country.reset()
    pie_currency.reset()
    //make sure we are not missing any field
    year=document.getElementById("item_list_year_forecast").value
    currency_list=document.getElementById("item_list_currency").value
    CFF_report_id=document.getElementById("list_report").value


    currency_list=currency_list.split(",")
    // We load it via a fetch in the API
    fetch(`/cash_forecast_change`, {
        method: 'POST',
        body: JSON.stringify({
            year : year,
            currency_list:currency_list, 
            CFF_report_id:CFF_report_id     
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
                spinner.style.display = "none"
            }
        })
}

function selectall(elm){
    var table = document.getElementById("dropdown_contract") 
    var checked_box_list=table.querySelectorAll('input[type=checkbox]') 
    var select_mode=elm.textContent 
    if (select_mode=="(select all)"){
        elm.textContent="(unselect all)"
        checked_status=true
    }else{
        elm.textContent="(select all)"
        checked_status=false
    }    

    imput_list=[]   
    //go throug list and selec or unselect all check box
    for (i = 0; i < checked_box_list.length; ++i) {
        checked_box_list[i].checked=checked_status
        span_element=checked_box_list[i].parentElement.children[1]
        imput_list.push(span_element.innerHTML)
        }
  
    if (checked_status== false)
        imput_list=[]
    //item_list_display_form_new_hidden.value=imput_list
    item_list_contract.value=imput_list
    accruals_change()
}


function selectall_forecast(elm){
    var table = document.getElementById("dropdown_currency") 
    var checked_box_list=table.querySelectorAll('input[type=checkbox]') 
    var select_mode=elm.textContent 
    if (select_mode=="(select all)"){
        elm.textContent="(unselect all)"
        checked_status=true
    }else{
        elm.textContent="(select all)"
        checked_status=false
    }    

    imput_list=[]   
    //go throug list and selec or unselect all check box
    for (i = 0; i < checked_box_list.length; ++i) {
        checked_box_list[i].checked=checked_status
        span_element=checked_box_list[i].parentElement.children[1]
        imput_list.push(span_element.innerHTML)
        }
    //alert(imput_list)
    if (checked_status== false)
        imput_list=[]
    //item_list_display_form_new_hidden.value=imput_list
    item_list_currency.value=imput_list
    item_list_display_currency.value=imput_list
    cash_forecast_change()
}
