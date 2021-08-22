
function end_function_message(){
    // display a message stating that it is saved
    //prepare the spinner

    saved_message=document.getElementById("saved_message")
    saved_message.style.display="block"
    setTimeout(function() { 
        saved_message.style.display = "None";
        location.reload()
        }, 1000)

}



function new_contract_file(elm){
    if (elm.files.length==0){return}
    //select the row and table
        table=document.getElementById(id="contract_file_table").children[1]
    //create new row
        var newRow = table.insertRow(-1);
    // column 0 select, clone and insert Select
        newCell = newRow.insertCell(0);
        newCell.setAttribute("hidden", "true");
        newCell.innerHTML=`<span >NEW</span>`
    // column 1 select, clone and insert Select
        var cln = elm.cloneNode(true);
        newCell = newRow.insertCell(1);
        newCell.setAttribute("hidden", "true");
        newCell.appendChild(cln)
    // column 2 select, clone and insert Select
        newCell = newRow.insertCell(2);
        newCell.innerHTML=`<span>${elm.files[0].name}</span>` 
    // column 3 select, clone and insert input
        newCell = newRow.insertCell(3);
        newCell.innerHTML=`<button   class="btn btn-sm btn-outline-danger" title="delete" onclick="delete_file(this)" style="border:0px" ><span class="bi bi-trash"></span></button>`
    elm.value = ""  




}

function delete_file(elm){
    tr_to_delete=elm.parentElement.parentElement
    smooth_remove_row_nodatatable(tr_to_delete) 
}



//table: contract_beneficiaries
function add_new_row_beneficiary(){
    //select the row and table
        new_beneficiary_tr=document.getElementById(id="new_beneficiary_tr")
        beneficiary_table=document.getElementById(id="beneficiary_table")
    //remove id and onchange action + unhide button
        new_beneficiary_tr.removeAttribute('id');
        new_beneficiary_tr.children[0].children[0].removeAttribute('onchange')
        new_beneficiary_tr.children[2].children[0].hidden=false
    //create new row
        var newRow = beneficiary_table.insertRow(-1);
        newRow.id="new_beneficiary_tr"
    // column 0 select, clone and insert Select
        var itm = document.getElementById("hidden_select").children[0];
        var cln = itm.cloneNode(true);
        newCell = newRow.insertCell(0);
        newCell.appendChild(cln)
        
    // column 1 select, clone and insert input
        itm = document.getElementById("hidden_percentage").children[0];
        cln = itm.cloneNode(true);
        newCell = newRow.insertCell(1);
        newCell.appendChild(cln)
    // column 2 select, clone and insert input
        itm = document.getElementById("hidden_button").children[0];
        cln = itm.cloneNode(true);
        newCell = newRow.insertCell(2);
        newCell.appendChild(cln)



}

function delete_row_beneficiary(elm){
    tr_to_delete=elm.parentElement.parentElement
    smooth_remove_row_nodatatable(tr_to_delete) 
}
function convert_percentage(elm){
  var num = Number(elm.value);
  elm.value=num.toFixed(2)
}


//table: rules
function add_row_tranche_rate(elm){

    //select the current row and table
        current_row=elm.parentElement
        table=current_row.parentElement
    // get row index:
        row_nb=current_row.rowIndex
    // check that "to" value is above "from"
        from_value_current=current_row.cells[0].innerHTML.split(',').join("")*1
        to_value_current_row= elm.children[0].value.split(',').join("")*1
        if (from_value_current >= to_value_current_row) {alert(' make sure the "to" value is above the "from" value' );return}       
    //remove onchange action ( so that the user to not add a new line everythime he changed the formulation)
        elm.removeAttribute('onchange')
    //copy hidden row
        hidden_row=document.getElementById(id="hidden_tranche_rate_row").children[0]
    // paste row at the last line of the table
        hidden_row_html=hidden_row.innerHTML      
        current_row.insertAdjacentHTML("afterend",hidden_row_html)
    // input From value next line 
        table.rows[row_nb].cells[0].innerHTML=elm.children[0].value // paste  
    // unhide delete row
        current_row.cells[3].children[0].hidden=false
}

function new_to_value_tranche_rate(elm){
    // check if row is an existing one, if not, we do nothing
      //select the current row and table
        current_row=elm.parentElement.parentElement
        table=current_row.parentElement
        row_nb=current_row.rowIndex// get row index:
        table_row_nb=table.rows.length// get row index:
        if (table_row_nb==row_nb) {return} // if nb row= current row, then it means its a new rw, and not an existing one

    // retreive the from and to of the current and previous row
        from_value_current=current_row.cells[0].innerHTML
        to_value_current_row= elm.value
        from_value_next_row=table.rows[row_nb].cells[0].innerHTML
        to_value_next_row=table.rows[row_nb].cells[1].children[0].value
    //check that "to" value is above "from"
        if (from_value_current.split(',').join("")*1 >= to_value_current_row.split(',').join("")*1) {
            alert(' make sure the "to" value is above the "from" value' );
            elm.value = from_value_next_row // here we retreive the value from the "from" of the following column
            return
            }
    //check that "to" value is below "to" of below row
        if (to_value_current_row.split(',').join("")*1 >= to_value_next_row.split(',').join("")*1 && to_value_next_row != ""){
            alert(' make sure the "to" value is is below the "to" value of below row' );  
            elm.value = from_value_next_row // here we retreive the value from the "from" of the following column
            return  
            }
        table.rows[row_nb].cells[0].innerHTML=to_value_current_row
}

function delete_row_tranche_rate(elm){
    //when a row is deleted, we copy the from value of the row we want to delete+ we delete the row: 
    current_row=elm.parentElement.parentElement
    table=current_row.parentElement
    from_value_deleted_row=current_row.cells[0].innerHTML
    row_nb=current_row.rowIndex
    table.rows[row_nb].cells[0].innerHTML=from_value_deleted_row
    smooth_remove_row_nodatatable(current_row)
}

function delete_rule(elm){
    tr_to_delete=elm.parentElement.parentElement
    smooth_remove_row_nodatatable(tr_to_delete) 
}


function thousands_separators(num)
  {
    var num_parts = num.toString().split(".");
    num_parts[0] = num_parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    return num_parts.join(".");
  }
  
function import_form_list(elm){

    elm.removeAttribute('onclick')
    
    //copy hidden row
        hidden_row=document.getElementById(id="import_form_list")
    //get dd_id:
        dd_id=elm.children[0].getAttribute("dd_id") 
    //replace form_new_hidden by form_new ( if 1 is the row nb) and ctry_new_hidden by ctry_new
        hidden_row_html=hidden_row.innerHTML.replace(/form_dynamic/g, dd_id).replace(/display: none/g,'display: block')
    // paste row at the last line of the table 
        elm.innerHTML = elm.innerHTML+ hidden_row_html
    // get value from input- it will be used to populate the dd
       formula_string=elm.children[0].children[1].value
       formula_list=formula_string.split(',')
    //select dd form
        dd_dubform=elm.children[1].children[1]
        li_list=dd_dubform.querySelectorAll('li')
    // check if li html includes <span>
    for (l in li_list){

        for (f in formula_list){
            if (li_list[l].innerHTML && li_list[l].innerHTML.includes(`<span>${formula_list[f]}</span>`)){
                li_list[l].children[0].checked=true
            }
        } 
    }
}

function import_country_list(elm){
    elm.removeAttribute('onclick')
    //copy hidden row
        hidden_row=document.getElementById(id="import_country_list")
    //get dd_id:
        dd_id=elm.children[0].getAttribute("dd_id") 
    //replace form_new_hidden by form_new ( if 1 is the row nb) and ctry_new_hidden by ctry_new
        hidden_row_html=hidden_row.innerHTML.replace(/ctry_dynamic/g, dd_id).replace(/display: none/g,'display: block')
    // paste row at the last line of the table 
        elm.innerHTML = elm.innerHTML+ hidden_row_html
    // get value from input- it will be used to populate the dd
       formula_string=elm.children[0].children[1].value
       formula_list=formula_string.split(',')
    //select dd form
        dd_subform=elm.children[1].children[1]
        li_list=dd_subform.querySelectorAll('li')
    // check if li html includes <span>
        for (l in li_list){
            for (f in formula_list){
                if (li_list[l].innerHTML && li_list[l].innerHTML.includes(`<span>${formula_list[f]}</span>`)){
                    li_list[l].children[0].checked=true
                }
            } 
    }
    //check uncheck all:
    formula_string_isall=elm.children[0].children[0].value
    if (formula_string_isall=="All" || formula_string_isall.includes("All except")){
        dd_subform.children[0].children[1].children[0].children[0].checked=true
    }
}

function import_qty_value_currency(elm){
    //parent element
        parent=elm.parentElement
    // save currency value
        curr=elm.value
    //copy hidden row
        item=document.getElementById(id="import_currency_list")
    // paste  
        elm.outerHTML =  item.innerHTML
    // select the drop down
        drop_down=parent.children[1]
    // change dd to current value
    option_to_select=drop_down.querySelectorAll(`option[value="${curr}"]`)[0]
    $(option_to_select).attr('selected',`selected`)
}


//table: Mini Gar
function hide_unhide_mini(elm){
    mini_table= document.getElementById('mini_table')

    if (elm.value == "YES"){
        mini_table.hidden=false

    }else{
        mini_table.hidden=true

    }
}


// general functions


function submit_validator_decision(reponse_validator){
    spinner_on()
    document.getElementById("reponse_validator").value=reponse_validator
    document.getElementById("reponse_validator_form").submit()
}



function submit_delete_contract_request(contract_id){
    alert(check_authentification())
    //first check if user is authentified, if not we log out
    fetch('/isauthenticated', {method: 'GET'})
        //retreive the partner ID  (result.partner_id ) and create the additional row
        .then(response => response.json())
        .then(result => {
            if (result.isauthenticated=="NO"){
                document.location.reload();
            }else{
                //prepare the spinner
                saved_message=document.getElementById("saved_message")
                spinner_on()
                //send detele request
                fetch(`/submit_delete_contract_request/${contract_id}`, {method: 'POST',})
                .then(response => response.json())
                .then(result => {
                    if (!!result.error) {
                        button.style.display="block";
                        spinner_off();
                        alert(result.error);
                        return;
                    }else{
                        end_function_message();
                        location.reload()  
                    }
                })    
            }     
        })  
}

function delete_contract(url){
        //prepare the spinner

        saved_message=document.getElementById("saved_message")
        button=document.getElementById("button")
        button.style.display="none"
        spinner_on()

        window.open(url,"_self");  

}
