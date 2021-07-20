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

function save_contract_partner(contract_id){

    //check if total =100
    beneficiary_table=document.getElementById(id="beneficiary_table")
    td_percent_list=beneficiary_table.querySelectorAll("input")
    td_select_list=beneficiary_table.querySelectorAll("select")
    
    length_table=td_percent_list.length-1
    var sum=0
    var import_array = []
    for (var i = 0; i < length_table; i++) {
        sum=Number(td_percent_list[i].value)+sum
        import_array.push(`[${td_select_list[i].value},"${td_percent_list[i].value}"]`)
    } 

    if(sum != 100){ 
        if ((td_select_list[0].value=="new") && (td_percent_list[0].value=="")){}else{
            alert(`the total of percentage is ${sum} instead of 100`)
            return
        }
    }
    //Select the spinner, save button and message
    spinner_beneficiary=document.getElementById("spinner_beneficiary")
    saved_button_beneficiary=document.getElementById(id="saved_button_beneficiary")
    saved_message_beneficiary=document.getElementById(id="saved_message_beneficiary")
    spinner_beneficiary.style.display = "Block"
    saved_button_beneficiary.style.display = "None"


    import_string="["+import_array+"]"
    // We load it via a fetch in the API
    fetch(`/save_contract_partner/${contract_id}`, {
        method: 'POST',
        body: import_string
        })
        .then(response => response.json())
        .then(result => {
            spinner_beneficiary.style.display = "None"
            if (!!result.error) {alert(result.error);return}
            //message
            saved_message_beneficiary.style.display = "Block"
            setTimeout(function() { 
                saved_message_beneficiary.style.display = "None",
                saved_button_beneficiary.style.display = "Block"
            },
            1000)
        })
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
function save_rule(contract_id){
    //Select the spinner, save button and message
    spinner_rule=document.getElementById("spinner_rule")
    saved_button_rule=document.getElementById(id="saved_button_rule")
    saved_message_rule=document.getElementById(id="saved_message_rule")
    spinner_rule.style.display = "Block"
    saved_button_rule.style.display = "None"

    
    main_list=[]
    sub_list=[]
    table=document.getElementById(id="rule_table").children[1]
    length_table=table.rows.length-1
    //if (length_table ==0){return}
    for (var i = 0; i < length_table; i++) {
        row=table.rows[i]
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
    //create main list before Fetch
    main_list.push('['+ sub_list+ ']')

    fetch(`/save_rule/${contract_id}`, {
        method: 'POST',
        body: main_list
        })
        .then(response => response.json())
        .then(result => {
            spinner_rule.style.display = "None"
            if (!!result.error) {alert(result.error);return}

            //message
            saved_message_rule.style.display = "Block"
            setTimeout(function() { 
                saved_message_rule.style.display = "None",
                saved_button_rule.style.display = "Block"
            },
                
            1000)

        })
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

function save_invoice_breakdown(contract_id){
  //check if total =100
    table=document.getElementById(id="sales_breakdown_table").children[1]
    length_table=table.rows.length

    var sublist = []
    for (var i = 0; i < length_table; i++) {
        id=table.rows[i].children[0].innerHTML
        sales_breakdown_contract_definition=table.rows[i].children[2].children[0].value
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
            //message
            saved_message=document.getElementById(id="saved_message_breakdown")
            saved_message.innerHTML="Saved"
            setTimeout(function() { 
                saved_message.innerHTML=""},
            1000)
        })
}


function new_contract_file(contract_id){

    //definition od the elements

    file_=document.getElementById("fileSelect")

    if (file_.files.length==0){return}
    name_file=file_.files[0].name
    file_value=file_.value
    //Select the spinner
    spinner_top=document.getElementById('central_spinner')
    spinner_top.style.display = "Block"


  
    let formData = new FormData();
    formData.append('name', name_file);
    formData.append('contract_id', contract_id);
    formData.append('file', file_.files[0], name_file);

    //book in database
    fetch('/new_contract_file', {
        method: 'POST',
        body: formData//JSON.stringify({name:name_value,acc_year:year_value,acc_month:month_id,})
        })
    //retreive the partner ID  (result.partner_id ) and create the additional row
        .then(response => response.json())
        .then(result => {

            if (result.error){
                alert(result.error)
            }else{
                cf_id=result.cf_id
                cf_url=result.cf_url
                document.getElementById("fileSelect").value = ""
                //select the row and table
                    table=document.getElementById(id="contract_file_table")
                //create new row
                    var newRow = table.insertRow(-1);
                // column 0 select, clone and insert Select
                    newCell = newRow.insertCell(0);
                    newCell.innerHTML=`<a href="${cf_url}" target="_blank" ><span class="fname">${name_file}</span></a>`  
                // column 1 select, clone and insert input
                    newCell = newRow.insertCell(1);
                    newCell.innerHTML=`<button   class="btn btn-sm btn-outline-danger" title="delete" onclick="delete_contract_file(this,${cf_id})" style="border:0px" ><span class="bi bi-trash"></span></button>`
            }
            spinner_top.style.display = "None"     
        })
    } 



function delete_contract_file(elm,cf_id) {
    fetch(`/delete_contract_file/${cf_id}`, {
        method: 'POST',})
    .then(response => response.json())
    .then(result => {
        if (result.error){
            alert(result.error)
        }else{
        elm.parentNode.parentNode.remove()
        }
    })

}

function hide_table(table){
    document.getElementById(table).hidden=true
    document.getElementById(`hide_${table}`).hidden=true
    document.getElementById(`unhide_${table}`).hidden=false
}
function unhide_table(table){
    document.getElementById(table).hidden=false
    document.getElementById(`hide_${table}`).hidden=false
    document.getElementById(`unhide_${table}`).hidden=true
}