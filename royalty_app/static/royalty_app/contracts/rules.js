
function end_function_message(){
    // display a message stating that it is saved
    //prepare the spinner

    spinner_completion.innerHTML= "90% :reloading page"
    setTimeout(function() { 
        location.reload()
        }, 1000)

}



function new_attachement(elm){
    if (elm.files.length==0){return}
    //select the row and table
        table=document.getElementById(id="writer_attachement").children[0].children[1]
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
        beneficiary_table=document.getElementById(id="writer_beneficiary").children[0]
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
        if (from_value_current >= to_value_current_row) {
            elm.children[0].value=''
            alert(' make sure the "to" value is above the "from" value' );
            return}       
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

    //replace form_new_hidden by form_new ( if 1 is the row nb) and form_new_hidden by form_new
        hidden_row_html=hidden_row.innerHTML
    // paste row at the last line of the table 
        elm.insertAdjacentHTML('beforeend',hidden_row_html)
    // 
        comboTreeDropDownContainer=elm.querySelector(".comboTreeDropDownContainer")
        comboTreeInputBox=elm.querySelector(".comboTreeInputBox")
        comboTreeHiddenBox=elm.querySelector(".comboTreeHiddenBox")
        comboTreeHiddenBox_list=comboTreeHiddenBox.value.split(', ')
        checkbox_list=comboTreeDropDownContainer.querySelectorAll('input[type=checkbox]')
        checkbox_list_length=checkbox_list.length
    for (ch = 0; ch < checkbox_list_length; ++ch) {
        if( comboTreeHiddenBox_list.includes(checkbox_list[ch].getAttribute("item_code") ) ){
            checkbox_list[ch].checked=true
        }
    }
}

function import_country_list(elm){
    elm.removeAttribute('onclick')
    //copy hidden row
        hidden_row=document.getElementById(id="import_country_list")

    //replace form_new_hidden by form_new ( if 1 is the row nb) and ctry_new_hidden by ctry_new
        hidden_row_html=hidden_row.innerHTML
    // paste row at the last line of the table 
        elm.insertAdjacentHTML('beforeend',hidden_row_html)

    // 
    comboTreeDropDownContainer=elm.querySelector(".comboTreeDropDownContainer")
    comboTreeInputBox=elm.querySelector(".comboTreeInputBox")
    comboTreeHiddenBox=elm.querySelector(".comboTreeHiddenBox")
    selection_mode_input =elm.querySelector(".selection_mode_input ")

    comboTreeHiddenBox_list=comboTreeHiddenBox.value.split(', ')
    checkbox_list=comboTreeDropDownContainer.querySelectorAll('input[type=checkbox]')
    checkbox_list_length=checkbox_list.length
    for (ch = 0; ch < checkbox_list_length; ++ch) {
        if( comboTreeHiddenBox_list.includes(checkbox_list[ch].getAttribute("item_code") ) ){
            checkbox_list[ch].checked=true
        }
    }
    //check uncheck all:
    country_string_isall=comboTreeInputBox.innerHTML
    if (selection_mode_input.value =="EXCLUDE"){
        select_all_box=selection_mode_input =elm.querySelector(".select_all_box ")
        select_all_box.checked=true
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
    option_to_select=drop_down.querySelector(`option[value="${curr}"]`)
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

function add_new_milestone(elm){
    //select the current row and table
        current_row=elm.parentElement
    //remove onchange action ( so that the user to not add a new line everythime he changed the formulation)
        elm.removeAttribute('onchange')
    // get row index:
        row_nb=document.getElementById("unique_row_number").innerHTML
        row_nb++
        document.getElementById("unique_row_number").innerHTML=row_nb
    //unhide delete button
        current_row.cells[7].children[0].hidden=false
    //copy hidden row
        hidden_row=document.getElementById(id="hidden_row_milestone").children[0]
        hidden_row_html=hidden_row.innerHTML
    // paste row at the last line of the table        
        current_row.insertAdjacentHTML("afterend",hidden_row_html)
}

function booked_milestone(elm){
    //select the current row and table
        current_row=elm.parentElement.parentElement
    //select booking and payment date
        market=current_row.cells[4].children[0]
        booking_date=current_row.cells[5].children[0]
        payment_date=current_row.cells[6].children[0]
    //hidde
        if (elm.value== "YES"){
            market.hidden=false
            booking_date.hidden=false
            payment_date.hidden=false
        }else{
            market.hidden=true
            booking_date.hidden=true
            payment_date.hidden=true    
        }    
}

function delete_row_milestone(elm){
    tr_to_delete=elm.parentElement.parentElement
    smooth_remove_row_nodatatable(tr_to_delete) 
}

const number_fetch_before_reload = 6


function save_contract(contract_id,save_type){
        
    //check that each table is properly done

        body=check_each_table()
        if (!body){
            spinner_off()
            return
        }
    //check we are still connected:
        spinner_completion.innerHTML="5% Check if still authenticated"
        fetch('/isauthenticated', {method: 'GET'})
            .then(response => response.json())
            .then(feedback => {
                if (feedback.isauthenticated=="NO"){document.location.reload()}
            })
    //prepare the spinner

        button=document.getElementById("button")
        button.style.display="none"

    //book the modification in views.py for each table
        //create the bodies:
            body_basic_info=body[0]
            body_contract_partner=body[1]
            body_milestone=body[2] 
            body_rule=body[3]
            body_mini_gar=body[4]
        //save contracts
            count=document.getElementById("count")
            count.value=0
            spinner_completion.innerHTML="5% save basic info"
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
                    var writer_attachement_table=document.getElementById("writer_attachement").children[0]
                    tbody_attachement=writer_attachement_table.children[1]
                    //attachement_table=document.getElementById(id="writer_attachement").children[1]
                    var length_table=tbody_attachement.rows.length

                    list_pdf=[]
                    nb_new=0
                    for (var i = 0; i < length_table; i++) {
                        row=tbody_attachement.rows[i]
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
                            //attachement_table=document.getElementById(id="writer_attachement").children[1]
                            var length_table=tbody_attachement.rows.length
                            if (!!result.error) {
                                alert(result.error);
                                location.reload();}
                            //if nb_new=0, it means that there are no new files to load, hence we can skip this part, else we must loop through the remaining of the list, from nb_new till the end of the table
                            if (nb_new==0){

                                count.value=Number(count.value)+1
                                spinner_completion.innerHTML= Math.round(count.value/(number_fetch_before_reload+1)*100) + "% :attachement(s) saved"
                                if (count.value==number_fetch_before_reload ){end_function_message()}
                                }else{
                                    
                                    from_new=length_table-nb_new

                                    for (var i = from_new; i < length_table; i++) {

                                        row=tbody_attachement.rows[i]
                                        id= row.cells[0].children[0].innerHTML
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
                                                if (count.value==number_fetch_before_reload ){end_function_message()}
                                            }
                                        })
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
                            spinner_completion.innerHTML= Math.round(count.value/(number_fetch_before_reload+1)*100) + "% : beneficiary(ies) saved"
                            if (count.value==number_fetch_before_reload ){end_function_message()}
                        })
                //save milestone
                    fetch(`/save_milestone/${contract_id}`, {
                        method: 'POST',
                        body: body_milestone
                        })
                        .then(response => response.json())
                        .then(result => {
                            if (!!result.error) {alert(result.error);location.reload();}
                            count.value=Number(count.value)+1
                            spinner_completion.innerHTML= Math.round(count.value/(number_fetch_before_reload+1)*100) + "% :Milestone(s) saved"
                            if (count.value==number_fetch_before_reload ){end_function_message()}
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
                            spinner_completion.innerHTML= Math.round(count.value/(number_fetch_before_reload+1)*100) + "% :rules saved"
                            if (count.value==number_fetch_before_reload ){end_function_message()}
                        })
                //save mini guar
                    fetch(`/save_mini/${contract_id}`, {
                        method: 'PUT',
                        body: body_mini_gar
                    }).then(response => response.json())
                        .then(result => { 
                            if (!!result.error) {alert(result.error);location.reload();}
                            count.value=Number(count.value)+1
                            spinner_completion.innerHTML= Math.round(count.value/(number_fetch_before_reload+1)*100) + "% :minimum garentee saved"
                            if (count.value==number_fetch_before_reload ){end_function_message()}
                        })  
                //save invoice breakdown
                    table_breakdown=document.getElementById(id="writer_sales_breakdown").children[0].children[1]
                    length_table=table_breakdown.rows.length

                    var sublist = []
                    for (var i = 0; i < length_table; i++) {
                        id=table_breakdown.rows[i].children[0].innerHTML
                        sales_breakdown_contract_definition=table_breakdown.rows[i].children[2].children[0].value
                        if (sales_breakdown_contract_definition != "") {
                            sublist.push(`{
                                "id":${id},
                                "sales_breakdown_contract_definition":"${sales_breakdown_contract_definition}"
                            }`)
                        }
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
                            spinner_completion.innerHTML= Math.round(count.value/(number_fetch_before_reload+1)*100) + "% :sales report breakdown"
                            if (count.value==number_fetch_before_reload ){end_function_message()}
                        })
            })

    //reload page
}

function check_each_table(){
    var contract_currency=document.getElementById("contract_currency").value
    //table: basic_info
        spinner_on()
        spinner_completion.innerHTML="0% Check consistancy data"
        //verify coherence data 
          contract_type_input=document.getElementById(id="contract_type")
          contract_type=contract_type_input.value
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
                        contract_type :contract_type,
                        contract_name : contract_name_input.value,
                        transaction_direction: transaction_direction_input.value,
                        division_id: division_input.value,   
                        division_via_id:division_via_input.value,
                        payment_terms:payment_terms, 
                        m3_brand:brand_input.value, 
                    })
    //table: Beneficiaries
        //verify coherence data
            beneficiary_table=document.getElementById(id="writer_beneficiary")
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
    //table: Milestone
        //verify coherence data
            milestone_table=document.getElementById(id="writer_milestone").children[0].children[1]
            length_table=milestone_table.rows.length-1
            var sub_list = []
            if (length_table!=0){
                for (var m = 0; m < length_table; m++) {
                //create sublist before looping 
                    
                    row=milestone_table.rows[m]
                    name_milestone=row.cells[0].children[0].value
                    amount=row.cells[1].children[0].value.split(',').join("")
                    currency=row.cells[2].children[0].value
                    booked=row.cells[3].children[0].value
                    market=row.cells[4].children[0].value
                    booking_date=row.cells[5].children[0].value
                    payment_date=row.cells[6].children[0].value
                    if (name_milestone=="" ||amount=="" || currency==""|| booked==""){
                        alert(`in milestone section : make sure you inserted some value for the name, amount, currency or booked`)
                        return
                    }
                    if (booked=="YES" && ( booking_date=="" || payment_date==""|| market=="") ){
                        alert(`in milestone section :make sure you fill in the dates and market`)
                        return
                    }

                    sub_list.push(`{
                        "name":"${name_milestone}",
                        "amount":"${amount}",
                        "currency":"${currency}",
                        "booked":"${booked}",
                        "market":"${market}",
                        "booking_date":"${booking_date}",
                        "payment_date":"${payment_date}"
                        }`)     
                } 
            }

        //prepare body
            body_milestone="["+sub_list+"]"

    //table: rules:
        //prepare basic data
        tbody_list=document.querySelectorAll(".tbody_writer")
        tbody_list_length=tbody_list.length

        writer_SALES=document.getElementById(id="writer_SALES")
        writer_COGS=document.getElementById(id="writer_COGS")
        writer_ROYALTY=document.getElementById(id="writer_ROYALTY")
        writer_MARGIN=document.getElementById(id="writer_MARGIN")
        main_list=[]
        sub_list=[]
        factor_contract_type=1
        
        //verify coherence         
            for (var tbody = 0; tbody < tbody_list_length; tbody++) {
                length_table=tbody_list[tbody].rows.length-1
                for (var i = 0; i < length_table; i++) {
                    row=tbody_list[tbody].rows[i]

                    formulation_InputWrapper= row.querySelector(".formulation")
                    formulation= formulation_InputWrapper.querySelector(".comboTreeHiddenBox ").value

                    country_InputWrapper= row.querySelector(".country")
                    country= country_InputWrapper.querySelector(".comboTreeHiddenBox").value
                    country_selection_mode = country_InputWrapper.querySelector(".selection_mode_input").value

                    period_from= row.querySelector(".period_from").value
                    period_to= row.querySelector(".period_to").value

                    if (period_from>period_to){
                        alert("in Rules section : make sure date from/to are coherent")
                        return
                    }
                    if (formulation==""){
                        alert("in Rules section : make sure you filed in the formulation fields ")
                        return  
                    }
                    if (country=="" & country_selection_mode == "INCLUDE"){
                        alert("in Rules section : make sure you filed in the country fields ")
                        return  
                    }
                }
            }


        // prepare data     
        if (contract_type == 2){ // 2 is the index number for MARG_ADJ
            factor_contract_type=-1
            // SALES Table
                //prepare body
                    tbody=writer_SALES.querySelector(".tbody_writer")
                    tbody_length=tbody.rows.length-1
                    for (var i = 0; i < tbody_length; i++) {
                            row=tbody.rows[i]
                        //Formulation
                            formulation_InputWrapper= row.querySelector(".formulation")
                            formulation= formulation_InputWrapper.querySelector(".comboTreeHiddenBox ").value
                            formulation=formulation.replaceAll(', ','","')
                        //Country & Incl-exclu
                            country_InputWrapper= row.querySelector(".country")
                            country= country_InputWrapper.querySelector(".comboTreeHiddenBox").value
                            country=country.replaceAll(', ','","')
                            country_selection_mode = country_InputWrapper.querySelector(".selection_mode_input").value
                        // period
                            period_from= row.querySelector(".period_from").value
                            period_to= row.querySelector(".period_to").value
                        // field_type
                            field_type= "RATE"
                        // tranche_type
                            tranche_type= "NO"
                        // Royalty
                            rate_value=100
                            qty_value=0
                            qty_value_currency=contract_currency
                            tranche_currency=contract_currency
                            tranche_list=[]

                        //create sublist before looping 
                            sub_list.push(`{
                                "rule_type":"SALES",
                                "tranche_currency":"${tranche_currency}",
                                "formulation":["${formulation}"],
                                "country_incl_excl":"${country_selection_mode}",
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
          
                
            // COGS Table
                //prepare body
                    tbody=writer_COGS.querySelector(".tbody_writer")
                    tbody_length=tbody.rows.length-1
                    for (var i = 0; i < tbody_length; i++) {
                        row=tbody.rows[i]
                        //Formulation
                            formulation_InputWrapper= row.querySelector(".formulation")
                            formulation= formulation_InputWrapper.querySelector(".comboTreeHiddenBox ").value
                            formulation=formulation.replaceAll(', ','","')
                        //Country & Incl-exclu
                            country_InputWrapper= row.querySelector(".country")
                            country= country_InputWrapper.querySelector(".comboTreeHiddenBox").value
                            country=country.replaceAll(', ','","')
                            country_selection_mode = country_InputWrapper.querySelector(".selection_mode_input").value
                        // period
                            period_from= row.querySelector(".period_from").value
                            period_to= row.querySelector(".period_to").value
                        // field_type
                            field_type= "QTY"
                        // tranche_type
                            tranche_type= "NO"
                        // Royalty
                            rate_value=0
                            qty_value=-row.querySelector(".qty_value").value.split(',').join("")
                            qty_value_currency=row.querySelector(".qty_value_currency").value
                            tranche_currency=contract_currency
                            tranche_list=[]

                        //create sublist before looping 
                            sub_list.push(`{
                                "rule_type":"COGS",
                                "tranche_currency":"${tranche_currency}",
                                "formulation":["${formulation}"],
                                "country_incl_excl":"${country_selection_mode}",
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
                
            // Margin Table
                //prepare body
                    tbody=writer_MARGIN.querySelector(".tbody_writer")
                    tbody_length=tbody.rows.length-1
                    for (var i = 0; i < tbody_length; i++) {
                        row=tbody.rows[i]
                        //Formulation
                            formulation_InputWrapper= row.querySelector(".formulation")
                            formulation= formulation_InputWrapper.querySelector(".comboTreeHiddenBox ").value
                            formulation=formulation.replaceAll(', ','","')
                        //Country & Incl-exclu
                            country_InputWrapper= row.querySelector(".country")
                            country= country_InputWrapper.querySelector(".comboTreeHiddenBox").value
                            country=country.replaceAll(', ','","')
                            country_selection_mode = country_InputWrapper.querySelector(".selection_mode_input").value
                        // period
                            period_from= row.querySelector(".period_from").value
                            period_to= row.querySelector(".period_to").value
                        // field_type
                            field_type= "RATE"
                        // tranche_type
                            tranche_type= row.querySelector(".tranche_type").value
                        // Royalty
                            rate_value=0
                            qty_value=0
                            qty_value_currency=contract_currency
                            tranche_currency=contract_currency
                            tranche_list=[]
                            if ((field_type =="RATE")&&(tranche_type=="NO")){//Rate
                                rate_value= -Number(row.querySelector(".rate_value").value)
                            }
                        //tranches
                            if ((field_type =="RATE")&&(tranche_type=="YES")){
                                tranche_tbody= row.querySelector(".tranche_tbody")
                                length_tranche_table=tranche_tbody.rows.length
                                for (var r = 0; r < length_tranche_table; r++) {
                                    row_tranche=tranche_tbody.rows[r]
                                    from_tranche=Number(row_tranche.querySelector(".from_tranche").innerHTML.split(',').join(""))
                                    to_tranche=Number(row_tranche.querySelector(".to_tranche").value.split(',').join(""))
                                    rate_tranche=-Number(row_tranche.querySelector(".rate_tranche").value)
                                    tranche_list.push(`{
                                        "from_tranche":${from_tranche},
                                        "to_tranche":${to_tranche},
                                        "rate_tranche":${rate_tranche}
                                    }`)
                                    if (r==0){
                                        rate_value=rate_tranche
                                    }
                                }
                                tranche_currency=row.querySelector(".tranche_currency").value
                            }
                            
                        //create sublist before looping 
                            sub_list.push(`{
                                "rule_type":"MARGIN",
                                "tranche_currency":"${tranche_currency}",
                                "formulation":["${formulation}"],
                                "country_incl_excl":"${country_selection_mode}",
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
            }

        // ROYALTY Table
            //prepare body
                tbody=writer_ROYALTY.querySelector(".tbody_writer")
                tbody_length=tbody.rows.length-1
                for (var i = 0; i < tbody_length; i++) {
                    row=tbody.rows[i]
                    //Formulation
                        formulation_InputWrapper= row.querySelector(".formulation")
                        formulation= formulation_InputWrapper.querySelector(".comboTreeHiddenBox ").value
                        formulation=formulation.replaceAll(', ','","')
                    //Country & Incl-exclu
                        country_InputWrapper= row.querySelector(".country")
                        country= country_InputWrapper.querySelector(".comboTreeHiddenBox").value
                        country=country.replaceAll(', ','","')
                        country_selection_mode = country_InputWrapper.querySelector(".selection_mode_input").value
                    // period
                        period_from= row.querySelector(".period_from").value
                        period_to= row.querySelector(".period_to").value
                    // field_type
                        field_type= row.querySelector(".field_type").value
                    // tranche_type
                        tranche_type= row.querySelector(".tranche_type").value
                    // Royalty
                        rate_value=0
                        qty_value=0
                        qty_value_currency=contract_currency
                        tranche_currency=contract_currency
                        tranche_list=[]
                        if ((field_type =="RATE")&&(tranche_type=="NO")){//Rate
                            rate_value= factor_contract_type*Number(row.querySelector(".rate_value").value)
                        }
                        if ((field_type =="QTY")&&(tranche_type=="NO")){//QTY
                            qty_value= factor_contract_type*Number(row.querySelector(".qty_value").value.split(',').join(""))
                            qty_value_currency=row.querySelector(".qty_value_currency").value
                        }
                    //tranches
                        if ((field_type =="RATE")&&(tranche_type=="YES")){
                            tranche_tbody= row.querySelector(".tranche_tbody")
                            length_tranche_table=tranche_tbody.rows.length
                            for (var r = 0; r < length_tranche_table; r++) {
                                row_tranche=tranche_tbody.rows[r]
                                from_tranche=Number(row_tranche.querySelector(".from_tranche").innerHTML.split(',').join(""))
                                to_tranche=Number(row_tranche.querySelector(".to_tranche").value.split(',').join(""))
                                rate_tranche=factor_contract_type*Number(row_tranche.querySelector(".rate_tranche").value)
                                tranche_list.push(`{
                                    "from_tranche":${from_tranche},
                                    "to_tranche":${to_tranche},
                                    "rate_tranche":${rate_tranche}
                                }`)
                                if (r==0){
                                    rate_value=rate_tranche
                                }
                            }
                            tranche_currency=row.querySelector(".tranche_currency").value
                        }
                        
                    //create sublist before looping 
                        sub_list.push(`{
                            "rule_type":"ROYALTY",
                            "tranche_currency":"${tranche_currency}",
                            "formulation":["${formulation}"],
                            "country_incl_excl":"${country_selection_mode}",
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

       
        //return 

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
    return [body_basic_info,body_contract_partner,body_milestone, body_rule, body_mini_gar]
}

function tranche_field_ROYALTY(elm){
    //find the row
    var row=elm.parentElement.parentElement
    var row_cells=row.children
    //find the qty-rate and tranche column
    var qty_rate= row_cells[4].children[0].value
    var tranche= row_cells[5].children[0].value
    var royalty_column=row_cells[6]
    royalty_column.children[0].hidden=true
    royalty_column.children[1].hidden=true
    royalty_column.children[2].hidden=true
    royalty_column.children[3].hidden=true

    if ( (qty_rate== "RATE") && (tranche=="NO")){
        royalty_column.children[0].hidden=false

    }else if ((qty_rate== "RATE") && (tranche =="YES")) {
        royalty_column.children[1].hidden=false

    }else if ((qty_rate== "QTY") && (tranche =="NO")) {
        royalty_column.children[2].hidden=false

    }else {
        royalty_column.children[3].hidden=false

    }
}

function add_new_row(elm,rule_type){
    //select the current row and table
        current_row=elm.parentElement
    //remove onchange action ( so that the user to not add a new line everythime he changed the formulation)
        elm.removeAttribute('onchange')
    // get row index:
        row_nb=document.getElementById("unique_row_number").innerHTML
        row_nb++
        document.getElementById("unique_row_number").innerHTML=row_nb
    //unhide delete button
        current_row.querySelector('.delete_button').hidden=false
        //current_row.cells[7].children[0].hidden=false
    //copy hidden row
        hidden_row=document.getElementById(id=`hidden_row_${rule_type}`).children[0]
    //replace form_new_hidden by form_new ( if 1 is the row nb) and ctry_new_hidden by ctry_new
        hidden_row_html=hidden_row.innerHTML.replaceAll(`new_${rule_type}`, `${rule_type}${row_nb}`)

    // paste row at the last line of the table        
        current_row.insertAdjacentHTML("afterend",hidden_row_html)
}


