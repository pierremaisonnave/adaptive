
function save_contract(contract_id,save_type){
    //check that each table is properly done
        body=check_each_table()
        if (!body){return}
    //prepare the spinner
        spinner=document.getElementById("spinner")
        saved_message=document.getElementById("saved_message")
        button=document.getElementById("button")
        button.style.display="none"
        spinner.style.display="block"

    //book the modification in views.py for each table
        //create the bodies:
            body_basic_info=body[0]
            body_contract_partner=body[1] 
            body_rule=body[2]
            body_mini_gar=body[3]
        //save contracts
            count=document.getElementById("count")
            count.value=0
            fetch(`/save_contract_basic_info/${contract_id}/${save_type}`, {
                method: 'POST',
                body: body_basic_info
                })
                .then(response => response.json())
                .then(result => {
                    if (!!result.error) {alert(result.error);location.reload();}
                    //if the save_type is "SUBMIT_CHANGE", then it means that
                    if (result.contract_proposal_id) {
                        contract_id=result.contract_proposal_id
                    }

                //save pdf file

                    contract_file_table=document.getElementById(id="contract_file_table").children[1]
                    length_table=contract_file_table.rows.length

                    list_pdf=[]
                    nb_new=0
                    for (var i = 0; i < length_table; i++) {
                        row=contract_file_table.rows[i]
                        id= row.cells[0].children[0].innerHTML
                        if (id!="NEW"){
                            list_pdf.push(id)
                            }else{nb_new=1+nb_new}
                    }
                    fetch(`/pdf_file_to_keep/${contract_id}`, {
                        method: 'POST',
                        body: JSON.stringify({
                            list : list_pdf,
                            })
                        })
                        .then(response => response.json())
                        .then(result => {
                            contract_file_table=document.getElementById(id="contract_file_table").children[1]
                            length_table=contract_file_table.rows.length
                            if (!!result.error) {
                                alert(result.error);
                                location.reload();}
                            if (nb_new==0){
                                count.value=Number(count.value)+1
                                if (count.value==5 ){end_function_message()}
                                }

                            for (var i = 0; i < length_table; i++) {
                                row=contract_file_table.rows[i]
                                id= row.cells[0].children[0].innerHTML
                                if (id=="NEW"){
                                    file_=row.cells[1].children[0]
                                    name_file=file_.files[0].name
                                    
                                    let formData = new FormData();
                                    formData.append('name', name_file);
                                    formData.append('contract_id', contract_id);
                                    formData.append('file', file_.files[0], name_file);
                                    //book in database
                                    fetch('/new_contract_file', {
                                        method: 'POST',
                                        body: formData//JSON.stringify({name:name_value,acc_year:year_value,acc_month:month_id,})
                                    })
                                    .then(response => response.json())
                                    .then(result => {
                                        nb_new=nb_new-1
                                        if (nb_new==0){
                                            count.value=Number(count.value)+1
                                            if (count.value==5 ){end_function_message()}
                                            }
                                            })
                                }else{

                                    if(i==length_table-1){
                                        count.value=Number(count.value)+1
                                        if (count.value==5 ){end_function_message()}
                                        }
                                }
                            }
                        })

                     // then it means that some contract must be copied/paste from Change to Proposal     

                    
                //save beneficiaries
                    fetch(`/save_contract_partner/${contract_id}`, {
                        method: 'POST',
                        body: body_contract_partner
                        })
                        .then(response => response.json())
                        .then(result => {
                            if (!!result.error) {alert(result.error);location.reload();}
                            count.value=Number(count.value)+1
                            if (count.value==5 ){end_function_message()}
                        })
                //save rules
                    fetch(`/save_rule/${contract_id}`, {
                        method: 'POST',
                        body: body_rule
                        })
                        .then(response => response.json())
                        .then(result => {
                            if (!!result.error) {alert(result.error);location.reload();}
                                            
                            count.value=Number(count.value)+1
                            if (count.value==5 ){end_function_message()}
                        })
                //save mini guar
                    fetch(`/save_mini/${contract_id}`, {
                        method: 'PUT',
                        body: body_mini_gar
                    }).then(response => response.json())
                        .then(result => { 
                            if (!!result.error) {alert(result.error);location.reload();}
                            count.value=Number(count.value)+1
                            if (count.value==5 ){end_function_message()}
                        })  
                //save invoice breakdown
                    table_breakdown=document.getElementById(id="sales_breakdown_table").children[1]
                    length_table=table_breakdown.rows.length

                    var sublist = []
                    for (var i = 0; i < length_table; i++) {
                        id=table_breakdown.rows[i].children[0].innerHTML
                        sales_breakdown_contract_definition=table_breakdown.rows[i].children[2].children[0].value
                        sublist.push(`{
                            "id":${id},
                            "sales_breakdown_contract_definition":"${sales_breakdown_contract_definition}"
                        }`)
                    } 

                    import_string="["+sublist+"]"
                    // We load it via a fetch in the API
                    fetch(`/save_invoice_breakdown/${contract_id}`, {
                        method: 'POST',
                        body: import_string
                        })
                        .then(response => response.json())
                        .then(result => {
                            if (!!result.error) {alert(result.error);return}
                            count.value=Number(count.value)+1
                            if (count.value==5 ){end_function_message()}
                        })
            })

    //reload page
}


function end_function_message(){
    // display a message stating that it is saved
    //prepare the spinner
    spinner=document.getElementById("spinner")
    saved_message=document.getElementById("saved_message")
    saved_message.style.display="block"
    spinner.style.display="none"
    setTimeout(function() { 
        saved_message.style.display = "None";
        location.reload()
        }, 1000)

}

function check_each_table(){
    //table: basic_info
        //verify coherence data 
          contract_name_input=document.getElementById(id="contract_name")
          division_input=document.getElementById(id="division")
          division_via_input=document.getElementById(id="division_via")
          transaction_direction_input=document.getElementById(id="transaction_direction")
          payment_terms_input=document.getElementById(id="payment_terms")
          payment_terms=payment_terms_input.value
          if (payment_terms==""){
                alert(`payment terms cannot be empty`)
                return
          }
          brand_input=document.getElementById(id="brand")
        //prepare body
            body_basic_info=JSON.stringify({
                        contract_name : contract_name_input.value,
                        transaction_direction: transaction_direction_input.value,
                        division_id: division_input.value,   
                        division_via_id:division_via_input.value,
                        payment_terms:payment_terms, 
                        m3_brand:brand_input.value, 
                    })
    //table: contract_partner
        //verify coherence data
            beneficiary_table=document.getElementById(id="beneficiary_table")
            td_percent_list=beneficiary_table.querySelectorAll("input")
            td_select_list=beneficiary_table.querySelectorAll("select")
            
            length_table=td_percent_list.length-1
            var sum=0
            var import_array = []
            if (length_table==0){
                    alert(`you must select at least one partner`)
                    return
                }
            for (var i = 0; i < length_table; i++) {
                sum=Number(td_percent_list[i].value)+sum
                import_array.push(`[${td_select_list[i].value},"${td_percent_list[i].value}"]`)
            } 

            if(sum != 100){ 
                if ((td_select_list[0].value=="new") && (td_percent_list[0].value=="")){}else{
                    alert(`in Beneficiaries section :the total of percentage is ${sum} instead of 100`)
                    return
                }
            }
        //prepare body
            body_contract_partner="["+import_array+"]"

    //table: rules:
        //verify coherence data
            rule_table=document.getElementById(id="rule_table").children[1]
            length_table=rule_table.rows.length-1
            for (var i = 0; i < length_table; i++) {
                row=rule_table.rows[i]
                country= row.cells[1].children[0].children[0].children[0].value
                period_from= row.cells[3].children[0].value
                period_to= row.cells[4].children[0].value
                if (period_from>period_to){
                    alert("in Rules section : make sure date from/to are coherent")
                    return
                }
                if (country==""){
                    alert("in Rules section : make sure you filed in the country fields ")
                    return  
                }
            }
        //prepare body
            main_list=[]
            sub_list=[]

            //if (length_table ==0){return}
            for (var i = 0; i < length_table; i++) {
                row=rule_table.rows[i]
                //Report_currency
                    Report_currency="same_as_contract"
                //Formulation
                    formulation= row.cells[0].children[0].children[0].children[0].value
                    formulation=formulation.replaceAll(',','","')

                //Country & Incl-exclu
                    country_list_untreated= row.cells[1].children[0].children[0].children[0].value

                    if ((country_list_untreated.substring(0, 10) == "All except")||(country_list_untreated=='All')){
                        country_incl_excl="EXCLUDE"
                        country_list_untreated=country_list_untreated.replace('All except : ', '').replace('All', '') 
                    }else {country_incl_excl="INCLUDE"}
                    country=country_list_untreated.replaceAll(',','","')
        
                // field_type
                    field_type= row.cells[2].children[0].value
                // period
                    period_from= row.cells[3].children[0].value
                    period_to= row.cells[4].children[0].value
                // tranche_type
                    tranche_type= row.cells[5].children[0].value
                // value
                    rate_value=0
                    qty_value=0
                    if ((field_type =="RATE")&&(tranche_type=="NO")){
                        rate_value= Number(row.cells[6].children[0].value)
                    }
                    if ((field_type =="QTY")&&(tranche_type=="NO")){
                        qty_value= Number(row.cells[8].children[0].value.split(',').join(""))
                    }
                //Report_currency
                    qty_value_currency=row.cells[8].children[1].value
                //tranches
                    var tranche_list=[]
                    if ((field_type =="RATE")&&(tranche_type=="YES")){
                        tranche_table= row.cells[7].children[0].children[1]
                        length_tranche_table=tranche_table.rows.length
                        for (var r = 0; r < length_tranche_table; r++) {
                            row_tranche=tranche_table.rows[r]
                            from_tranche=Number(row_tranche.cells[0].innerHTML.split(',').join(""))
                            to_tranche=Number(row_tranche.cells[1].children[0].value.split(',').join(""))
                            rate_tranche=Number(row_tranche.cells[2].children[0].value)
                            tranche_list.push(`{
                                "from_tranche":${from_tranche},
                                "to_tranche":${to_tranche},
                                "rate_tranche":${rate_tranche}
                            }`)
                            if (r==0){
                                rate_value=rate_tranche
                            }
                        }
                    }
                
                //create sublist before looping 
                    sub_list.push(`{
                        "Report_currency":"${Report_currency}",
                        "formulation":["${formulation}"],
                        "country_incl_excl":"${country_incl_excl}",
                        "country":["${country}"],
                        "field_type":"${field_type}",
                        "period_from":"${period_from}",
                        "period_to":"${period_to}",
                        "tranche_type":"${tranche_type}",
                        "rate_value":${rate_value},
                        "qty_value":${qty_value},
                        "qty_value_currency":"${qty_value_currency}",
                        "tranche_list":[${tranche_list}]
                        }`)     
                }  
            main_list.push('['+ sub_list+ ']')
            body_rule=main_list
    //table: mini
        //verify coherence data
            mini_gar_status=document.getElementById('mini_gar_status')
            mini_gar_from=document.getElementById('mini_gar_from')
            mini_gar_to=document.getElementById('mini_gar_to')
            minimum_guar_remaining_allocation_country=document.getElementById('minimum_guar_remaining_allocation_country')
            minimum_guar_amount=document.getElementById('minimum_guar_amount')

            if (mini_gar_status.value=="NO"){
                minimum_guar_remaining_allocation_country.value=""
                minimum_guar_amount.value=""
                mini_gar_from.value=1900
                mini_gar_to.value=2100
            }else{
                if (mini_gar_from.value>mini_gar_to.value){
                    alert("in Mini Gar section: Date 'From' must be before date 'to'")
                    return
                }
                if (mini_gar_from.value=="" || mini_gar_to.value==""){
                    alert(" in Mini Gar section:year fields are empty")
                    return
                }
            }
        //prepare body
            body_mini_gar=JSON.stringify({
                        country_id : minimum_guar_remaining_allocation_country.value,
                        amount: Number(minimum_guar_amount.value.split(',').join("")),
                        mini_gar_status: mini_gar_status.value,   
                        mini_gar_from:mini_gar_from.value,
                        mini_gar_to:mini_gar_to.value  , 
                    })
    return [body_basic_info,body_contract_partner, body_rule, body_mini_gar]
}

//table: pdf contracts


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
    elm.parentNode.parentNode.remove()
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
    elm.parentNode.parentNode.remove()
}
function convert_percentage(elm){
  var num = Number(elm.value);
  elm.value=num.toFixed(2)
}



function qty_rate_tranche_change(elm){
    //find the row
    var row=elm.parentElement.parentElement
    var row_cells=row.children
    //find the qty-rate and tranche column
    var qty_rate= row_cells[2].children[0].value
    var tranche= row_cells[5].children[0].value

    row_cells[6].hidden=true
    row_cells[7].hidden=true
    row_cells[8].hidden=true
    row_cells[9].hidden=true
    if ( (qty_rate== "RATE") && (tranche=="NO")){
        row_cells[6].hidden=false

    }else if ((qty_rate== "RATE") && (tranche =="YES")) {
        row_cells[7].hidden=false

    }else if ((qty_rate== "QTY") && (tranche =="NO")) {
        row_cells[8].hidden=false

    }else {
        row_cells[9].hidden=false

    }
}

function add_new_cp(elm){
    //select the current row and table
        current_row=elm.parentElement
    //remove onchange action ( so that the user to not add a new line everythime he changed the formulation)
        elm.removeAttribute('onchange')
    // get row index:
        row_nb=document.getElementById("unique_row_number").innerHTML
        row_nb++
        document.getElementById("unique_row_number").innerHTML=row_nb
    //unhide delete button
        current_row.cells[10].children[0].hidden=false
    //
    //copy hidden row
        hidden_row=document.getElementById(id="hidden_cp_row").children[0]
    //replace form_new_hidden by form_new ( if 1 is the row nb) and ctry_new_hidden by ctry_new
        hidden_row_html=hidden_row.innerHTML.replace(/form_new_hidden/g, `form_${row_nb}`).replace(/ctry_new_hidden/g, `ctry_${row_nb}`)
    // paste row at the last line of the table        
        current_row.insertAdjacentHTML("afterend",hidden_row_html)
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
    current_row.remove()
    table.rows[row_nb-1].cells[0].innerHTML=from_value_deleted_row
}

function delete_rule(elm){
    elm.parentElement.parentElement.remove()
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
    document.getElementById("reponse_validator").value=reponse_validator
    document.getElementById("reponse_validator_form").submit()
}

function submit_delete_contract_request(contract_id){
        //prepare the spinner
        spinner=document.getElementById("spinner")
        saved_message=document.getElementById("saved_message")
        button=document.getElementById("button")
        button.style.display="none"
        spinner.style.display="block"

        fetch(`/submit_delete_contract_request/${contract_id}`, {
        method: 'POST',
        })
        .then(response => response.json())
        .then(result => {
            
            if (!!result.error) {
                button.style.display="block"
                spinner.style.display="none"
                alert(result.error);
                return;}else{
                    end_function_message()
                    location.reload()  
                }
        })

}