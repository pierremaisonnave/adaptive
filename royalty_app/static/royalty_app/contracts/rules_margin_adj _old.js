const number_fetch_before_reload = 6
function save_contract(contract_id,save_type){
    //check that each table is properly done
        body=check_each_table()
        if (!body){return}
    //check we are still connected:
        fetch('/isauthenticated', {method: 'GET'})
        .then(response => response.json())
        .then(feedback => {
            if (feedback.isauthenticated=="NO"){document.location.reload()}
        })
    //prepare the spinner

        saved_message=document.getElementById("saved_message")
        button=document.getElementById("button")
        button.style.display="none"
        spinner_on()

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
                            //if nb_new=0, it means that there are no new files to load, hence we can skip this part, else we must loop through the remaining of the list, from nb_new till the end of the table
                            if (nb_new==0){
                                count.value=Number(count.value)+1
                                if (count.value==number_fetch_before_reload ){end_function_message()}
                                }else{
                                    from_new=length_table-nb_new
                                    for (var i = from_new; i < length_table; i++) {
                                        row=contract_file_table.rows[i]
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
                            if (count.value==number_fetch_before_reload ){end_function_message()}
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
                            if (count.value==number_fetch_before_reload ){end_function_message()}
                        })
            })

    //reload page
}

function check_each_table(){
    //table: basic_info
        //verify coherence data 
          contract_type_input=document.getElementById(id="contract_type")
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
                        contract_type : contract_type_input.value,
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
    //table: Milestone
        //verify coherence data
        milestone_table=document.getElementById(id="milestone_table").children[1]
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
        //verify if contract is a MARGIN_ADJ type:

 
        //verify coherence data SALES
            SALES_table=document.getElementById(id="SALES_table").children[1]
            length_table_SALES=SALES_table.rows.length-1
            for (var i = 0; i < length_table_SALES; i++) {
                row=SALES_table.rows[i]
                country= row.cells[1].children[0].children[0].children[0].value
                period_from= row.cells[2].children[0].value
                period_to= row.cells[3].children[0].value
                if (period_from>period_to){
                    alert("in Rules section : make sure date from/to are coherent")
                    return
                }
                if (country==""){
                    alert("in Rules section : make sure you filed in the country fields ")
                    return  
                }
            }
        //verify coherence data COGS
            COGS_table=document.getElementById(id="COGS_table").children[1]
            length_table_COGS=COGS_table.rows.length-1
            for (var i = 0; i < length_table_COGS; i++) {
                row=COGS_table.rows[i]
                country= row.cells[1].children[0].children[0].children[0].value
                period_from= row.cells[2].children[0].value
                period_to= row.cells[3].children[0].value
                if (period_from>period_to){
                    alert("in Rules section: make sure date from/to are coherent")
                    return
                }
                if (country==""){
                    alert("in Rules section : make sure you filed in the country fields ")
                    return  
                }
            }
        //verify coherence data MARGIN
            MARGIN_table=document.getElementById(id="MARGIN_table").children[1]
            length_table_MARGIN=MARGIN_table.rows.length-1
            for (var i = 0; i < length_table_MARGIN; i++) {
                row=MARGIN_table.rows[i]
                country= row.cells[1].children[0].children[0].children[0].value
                period_from= row.cells[2].children[0].value
                period_to= row.cells[3].children[0].value
                if (period_from>period_to){
                    alert("in Rules section: make sure date from/to are coherent")
                    return
                }
                if (country==""){
                    alert("in Rules section : make sure you filed in the country fields ")
                    return  
                }
            }
    
        //verify coherence data ROYALTY
            ROYALTY_table=document.getElementById(id="ROYALTY_table").children[1]
            length_table_ROYALTY=ROYALTY_table.rows.length-1
            for (var i = 0; i < length_table_ROYALTY; i++) {
                row=ROYALTY_table.rows[i]
                country= row.cells[1].children[0].children[0].children[0].value
                period_from= row.cells[2].children[0].value
                period_to= row.cells[3].children[0].value
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
            //for SALES
                for (var i = 0; i < length_table_SALES; i++) {
                    row=SALES_table.rows[i]

                    //Formulation
                        formulation= row.cells[0].children[0].children[0].children[0].value
                        formulation=formulation.replaceAll(',','","')

                    //Country & Incl-exclu
                        country_list_untreated= row.cells[1].children[0].children[0].children[0].value

                        if ((country_list_untreated.substring(0, 10) == "All except")||(country_list_untreated=='All')){
                            country_incl_excl="EXCLUDE"
                            country_list_untreated=country_list_untreated.replace('All except : ', '').replace('All', '') 
                        }else {country_incl_excl="INCLUDE"}

                        country=country_list_untreated.replaceAll(', ',',').replaceAll(',','","') //for some reason, the contract_list is diyplayed with a space : "USA, CAD, .."--> we need to remove this space, on top of that, we must place "" between each country

                    // period
                        period_from= row.cells[2].children[0].value
                        period_to= row.cells[3].children[0].value

                    //create sublist before looping 
                        sub_list.push(`{
                            "rule_type":"SALES",
                            "tranche_currency":"same_as_contract",
                            "formulation":["${formulation}"],
                            "country_incl_excl":"${country_incl_excl}",
                            "country":["${country}"],
                            "field_type":"RATE",
                            "period_from":"${period_from}",
                            "period_to":"${period_to}",
                            "tranche_type":"NO",
                            "rate_value":100,
                            "qty_value":0,
                            "qty_value_currency":"USD",
                            "tranche_list":[]
                            }`)     
                    }  
            //for COGS
                for (var i = 0; i < length_table_COGS; i++) {
                    row=COGS_table.rows[i]

                    //Formulation
                        formulation= row.cells[0].children[0].children[0].children[0].value
                        formulation=formulation.replaceAll(',','","')

                    //Country & Incl-exclu
                        country_list_untreated= row.cells[1].children[0].children[0].children[0].value
                        if ((country_list_untreated.substring(0, 10) == "All except")||(country_list_untreated=='All')){
                            country_incl_excl="EXCLUDE"
                            country_list_untreated=country_list_untreated.replace('All except : ', '').replace('All', '') 
                        }else {country_incl_excl="INCLUDE"}

                        country=country_list_untreated.replaceAll(', ',',').replaceAll(',','","') //for some reason, the contract_list is diyplayed with a space : "USA, CAD, .."--> we need to remove this space, on top of that, we must place "" between each country

                    // period
                        period_from= row.cells[2].children[0].value
                        period_to= row.cells[3].children[0].value

                    // value
                        qty_value= -Number(row.cells[4].children[0].value.split(',').join(""))

                    //qty_value_currency
                        qty_value_currency=row.cells[4].children[1].value
    
                    //create sublist before looping 
                        sub_list.push(`{
                            "rule_type":"COGS",
                            "tranche_currency":"same_as_contract",
                            "formulation":["${formulation}"],
                            "country_incl_excl":"${country_incl_excl}",
                            "country":["${country}"],
                            "field_type":"QTY",
                            "period_from":"${period_from}",
                            "period_to":"${period_to}",
                            "tranche_type":"NO",
                            "rate_value":0,
                            "qty_value":${qty_value},
                            "qty_value_currency":"${qty_value_currency}",
                            "tranche_list":[]
                            }`)     
                    }

            //for ROYALTY
                for (var i = 0; i < length_table_ROYALTY; i++) {
                    row=ROYALTY_table.rows[i]

                    //Formulation
                        formulation= row.cells[0].children[0].children[0].children[0].value
                        formulation=formulation.replaceAll(',','","')

                    //Country & Incl-exclu
                        country_list_untreated= row.cells[1].children[0].children[0].children[0].value

                        if ((country_list_untreated.substring(0, 10) == "All except")||(country_list_untreated=='All')){
                            country_incl_excl="EXCLUDE"
                            country_list_untreated=country_list_untreated.replace('All except : ', '').replace('All', '') 
                        }else {country_incl_excl="INCLUDE"}

                        country=country_list_untreated.replaceAll(', ',',').replaceAll(',','","') //for some reason, the contract_list is diyplayed with a space : "USA, CAD, .."--> we need to remove this space, on top of that, we must place "" between each country
                    // period
                        period_from= row.cells[2].children[0].value
                        period_to= row.cells[3].children[0].value
                    // field_type
                        field_type= row.cells[4].children[0].value
                    // tranche_type
                        tranche_type= row.cells[5].children[0].value
                    // value
                        rate_value=0
                        qty_value=0
                        if ((field_type =="RATE")&&(tranche_type=="NO")){
                            rate_value= -Number(row.cells[6].children[0].value)
                        }
                        if ((field_type =="QTY")&&(tranche_type=="NO")){
                            qty_value= -Number(row.cells[8].children[0].value.split(',').join(""))
                        }
                    //qty_value_currency
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
                                rate_tranche=-Number(row_tranche.cells[2].children[0].value)
                                tranche_list.push(`{
                                    "from_tranche":${from_tranche},
                                    "to_tranche":${to_tranche},
                                    "rate_tranche":${rate_tranche}
                                }`)
                                if (r==0){
                                    rate_value=rate_tranche
                                }
                            }
                            tranche_currency=row.cells[7].children[0].children[0].children[0].children[3].children[0].value

                        }else{
                            //tranche_currency
                            tranche_currency="same_as_contract"
                        }

                    //create sublist before looping 
                        sub_list.push(`{
                            "rule_type":"ROYALTY",
                            "tranche_currency":"${tranche_currency}",
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

            //for MARGIN
                for (var i = 0; i < length_table_MARGIN; i++) {
                    row=MARGIN_table.rows[i]

                    //Formulation
                        formulation= row.cells[0].children[0].children[0].children[0].value
                        formulation=formulation.replaceAll(',','","')

                    //Country & Incl-exclu
                        country_list_untreated= row.cells[1].children[0].children[0].children[0].value

                        if ((country_list_untreated.substring(0, 10) == "All except")||(country_list_untreated=='All')){
                            country_incl_excl="EXCLUDE"
                            country_list_untreated=country_list_untreated.replace('All except : ', '').replace('All', '') 
                        }else {country_incl_excl="INCLUDE"}

                        country=country_list_untreated.replaceAll(', ',',').replaceAll(',','","') //for some reason, the contract_list is diyplayed with a space : "USA, CAD, .."--> we need to remove this space, on top of that, we must place "" between each country

                    // period
                        period_from= row.cells[2].children[0].value
                        period_to= row.cells[3].children[0].value
                    // tranche_type
                        tranche_type= row.cells[4].children[0].value
                    // value
                        rate_value=0
                        if (tranche_type=="NO"){
                            rate_value= -Number(row.cells[5].children[0].value)
                        }
                    //tranches
                        var tranche_list=[]
                        if ((field_type =="RATE")&&(tranche_type=="YES")){
                            tranche_table= row.cells[6].children[0].children[1]
                            length_tranche_table=tranche_table.rows.length
                            for (var r = 0; r < length_tranche_table; r++) {
                                row_tranche=tranche_table.rows[r]
                                from_tranche=Number(row_tranche.cells[0].innerHTML.split(',').join(""))
                                to_tranche=Number(row_tranche.cells[1].children[0].value.split(',').join(""))
                                rate_tranche=-Number(row_tranche.cells[2].children[0].value)
                                tranche_list.push(`{
                                    "from_tranche":${from_tranche},
                                    "to_tranche":${to_tranche},
                                    "rate_tranche":${rate_tranche}
                                }`)
                                if (r==0){
                                    rate_value=rate_tranche
                                }
                            }
                            tranche_currency=row.cells[6].children[0].children[0].children[0].children[3].children[0].value

                        }else{
                            //tranche_currency
                            tranche_currency="same_as_contract"
                        }

                    //create sublist before looping 
                        sub_list.push(`{
                            "rule_type":"MARGIN",
                            "tranche_currency":"${tranche_currency}",
                            "formulation":["${formulation}"],
                            "country_incl_excl":"${country_incl_excl}",
                            "country":["${country}"],
                            "field_type":"RATE",
                            "period_from":"${period_from}",
                            "period_to":"${period_to}",
                            "tranche_type":"${tranche_type}",
                            "rate_value":${rate_value},
                            "qty_value":0,
                            "qty_value_currency":"USD",
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
    return [body_basic_info,body_contract_partner,body_milestone, body_rule, body_mini_gar]
}

function tranche_field_ROYALTY(elm){
    //find the row
    var row=elm.parentElement.parentElement
    var row_cells=row.children
    //find the qty-rate and tranche column
    var qty_rate= row_cells[4].children[0].value
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
function tranche_field_MARGIN(elm){
    //find the row
    var row=elm.parentElement.parentElement
    var row_cells=row.children
    //find the qty-rate and tranche column
    var tranche= row_cells[4].children[0].value

    row_cells[5].hidden=true
    row_cells[6].hidden=true

    if (tranche=="NO"){
        row_cells[5].hidden=false
    }else {
        row_cells[6].hidden=false

    }
}
function add_new_MARGIN(elm){
    //select the current row and table
        current_row=elm.parentElement
    //remove onchange action ( so that the user to not add a new line everythime he changed the formulation)
        elm.removeAttribute('onchange')
    // get row index:
        row_nb=document.getElementById("unique_row_number").innerHTML
        row_nb++
        document.getElementById("unique_row_number").innerHTML=row_nb
    //unhide delete button
        current_row.cells[5].children[0].hidden=false
    //copy hidden row
        hidden_row=document.getElementById(id="hidden_row_MARGIN").children[0]
    //replace form_new_hidden by form_new ( if 1 is the row nb) and ctry_new_hidden by ctry_new
        hidden_row_html=hidden_row.innerHTML.replace(/form_new_MARGIN/g, `form_MARGIN${row_nb}`).replace(/ctry_new_MARGIN/g, `ctry_MARGIN${row_nb}`) 
    // paste row at the last line of the table        
        current_row.insertAdjacentHTML("afterend",hidden_row_html)
}
function add_new_COGS(elm){
    //select the current row and table
        current_row=elm.parentElement
    //remove onchange action ( so that the user to not add a new line everythime he changed the formulation)
        elm.removeAttribute('onchange')
    // get row index:
        row_nb=document.getElementById("unique_row_number").innerHTML
        row_nb++
        document.getElementById("unique_row_number").innerHTML=row_nb
    //unhide delete button
        current_row.cells[5].children[0].hidden=false
    //copy hidden row
        hidden_row=document.getElementById(id="hidden_row_COGS").children[0]
    //replace form_new_hidden by form_new ( if 1 is the row nb) and ctry_new_hidden by ctry_new
        hidden_row_html=hidden_row.innerHTML.replace(/form_new_COGS/g, `form_COGS${row_nb}`).replace(/ctry_new_COGS/g, `ctry_COGS${row_nb}`) 
    // paste row at the last line of the table        
        current_row.insertAdjacentHTML("afterend",hidden_row_html)
}
function add_new_SALES(elm){
    //select the current row and table
        current_row=elm.parentElement
    //remove onchange action ( so that the user to not add a new line everythime he changed the formulation)
        elm.removeAttribute('onchange')
    // get row index:
        row_nb=document.getElementById("unique_row_number").innerHTML
        row_nb++
        document.getElementById("unique_row_number").innerHTML=row_nb
    //unhide delete button
        current_row.cells[4].children[0].hidden=false
    //copy hidden row
        hidden_row=document.getElementById(id="hidden_row_SALES").children[0]
    //replace form_new_hidden by form_new ( if 1 is the row nb) and ctry_new_hidden by ctry_new
        hidden_row_html=hidden_row.innerHTML.replace(/form_new_SALES/g, `form_SALES${row_nb}`).replace(/ctry_new_SALES/g, `ctry_SALES${row_nb}`) 
    // paste row at the last line of the table        
        current_row.insertAdjacentHTML("afterend",hidden_row_html)
}
function add_new_ROYALTY(elm){
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
    //copy hidden row
        hidden_row=document.getElementById(id="hidden_row_ROYALTY").children[0]
    //replace form_new_hidden by form_new ( if 1 is the row nb) and ctry_new_hidden by ctry_new
        hidden_row_html=hidden_row.innerHTML.replace(/form_new_ROYALTY/g, `form_ROYALTY${row_nb}`).replace(/ctry_new_ROYALTY/g, `ctry_ROYALTY${row_nb}`)
    // paste row at the last line of the table        
        current_row.insertAdjacentHTML("afterend",hidden_row_html)
}
