
document.addEventListener('DOMContentLoaded', function() {
    var t0 = performance.now()

    //--------------------Initialization of Datatable ---------------------
    //the datatable is imported, and ordered
    $('#contracts_table').DataTable({
        "aaSorting": [[ 0, "desc" ]],
        columnDefs: [{ orderable: false, targets: [0,1,2,3,4,5,6,7,8,9,10,11,12] }],
    })

    document.querySelector("main").style.visibility = "visible";
    //the datatable automatically generate a filter button, we do not need it ( as we have search bar for each column)
    document.getElementById("contracts_table_filter").hidden=true
    var table = $('#contracts_table').DataTable();

    // when we select a search item, the following element must take place
    $('.fname2').on( 'keyup', function () {
        var column_nb=this.getAttribute("column")
        if ( ['2','3','4','5','7','9','11'].includes(column_nb)) {searched_value=`searched_value:${this.value}`} else {searched_value=this.value}
        
        table
            .columns( column_nb )
            .search( searched_value  )
            .draw();
        } 
    );
    //----------------------------------------------------------------------   
  
    // event to be taken when an object in the table is modified:
    document.addEventListener('change', event => {
        
        if (is_in_tbody(event)==false) { return;} // if we modify the form, the below code should not take place

        //the change and cancel button at the end of the list should be made visible + the background of the cell should be yellowed
        element= event.target
        var contract_id = element.getAttribute("contract_id") 
        document.getElementById(`change_${contract_id}`).hidden=false
        document.getElementById(`cancel_${contract_id}`).hidden=false
        element.parentElement.style.backgroundColor  = "#f2dfa1"

    //When the user modiy the input box , or the dropdown, we also need to update the hidden span located in the same cell- indeed, the search box at the top of each column look for the value in the span, not in the input
        //Country
        span_element=document.getElementById("span_"+element.id)
        element_id=element.id
        //if the cell contains a dropdown box:
        if (isadropdownlist(element_id)){
            //we first need to remove the selected from the previous option ( otherwise it remains)- for a reason I cannot explain, even though the user has selected a different country, the HTML do not show the "Selected"
                currently_selected_option=element.querySelectorAll(`option[selected="selected"]`)[0]
                currently_selected_option.removeAttribute("selected")
            // We get the text value of the selected option
                selected_option=element.options[element.selectedIndex]
                value_option=selected_option.text
            // then we paste it in the hidden span- The searched box loop through the table, and filter based on whether the searched item is in the cell. As the drop down box, has all the countries, no matter what we enter in the search bar, the row will be hidden-
            // the trick consit on searching based on "searched_value:+country_name " ( see JS " $('.fname2').on( 'keyup', function ()" here above)
                span_element.innerHTML="searched_value:"+value_option 
                selected_option.setAttribute('selected','selected')
        }
        //for the amount, we must remove the comma for the span
        else if (element_id.includes("minimum_guar_amount_")){
            value_without_comma=element.value.split(',').join("")
            span_element.innerHTML=value_without_comma
            $(element).attr('value',element.value)  
        }
        //for Name and nb day
        else {
            span_element.innerHTML=element.value
            $(element).attr('value',element.value)
        }
        //once the modification has been done in the DOM ( here above) we also must do the modif in the Datatable ( so that we can apply filter and other JQuery)   
        modification_=element.parentElement.innerHTML//
        var t = $('#contracts_table').DataTable() 
        t.cell(element.parentElement).data(modification_).draw(false)

    })

})


function delete_row_contract(contract_id) {
    var t = $('#contracts_table').DataTable()
    var r = confirm("Are you sure!");
    if (r == true) {
        fetch(`/delete_row_contract/${contract_id}`, {
            method: 'POST',})
        .then(response => response.json())
        .then(result => {
            if (result.error){
                alert(result.error)
            }else{
                tr_to_delete=document.getElementById(`contract_${contract_id}`) 
                t.row( tr_to_delete ).remove().draw(false);
            }
        })
    } 
}

function cancel_row_contract(contract_id,elm){
    //Everytime the user decides to cancel a modification, we must go thought a 3 steps approach
    //firts, we must get the original info from the database, through a fetch, Second, we modify the DOM, Thirds we load it in the Database
    fetch(`/cancel_row_contract/${contract_id}`)
    //First, get the info from database
    .then(response => response.json())
    .then(result => {
    //------------------------------------------------------------------------
        //Second, populate the page based on the info extracted from the databse
        //we first need to unhide all columns
        unhide_column()
        //Name
            document.getElementById(`span_contract_name_${contract_id}`).innerHTML=result.contract_name
            document.getElementById(`contract_name_${contract_id}`).setAttribute("value",`${result.contract_name}`)
        // transaction_direction
            //Span
                document.getElementById(`span_transaction_direction_${contract_id}`).innerHTML="searched_value:"+result.transaction_direction
            //Select
                var select_item= document.getElementById(`transaction_direction_${contract_id}`)
                //we first need to remove the selected from the previous option ( otherwise it remains)
                    currently_selected_option=select_item.querySelectorAll(`option[selected="selected"]`)[0]
                    currently_selected_option.removeAttribute("selected")
                //the finally insert the selection in the newly selected option
                    select_item.value=result.transaction_direction // we select the option
                    selected_option=select_item.options[select_item.selectedIndex] // after option is selected, we insert 'selected'
                    selected_option.setAttribute('selected','selected')
        // Division
            //Span
                document.getElementById(`span_division_${contract_id}`).innerHTML="searched_value:"+result.division_id
            //Select
                var select_item= document.getElementById(`division_${contract_id}`)
                //we first need to remove the selected from the previous option ( otherwise it remains)
                    currently_selected_option=select_item.querySelectorAll(`option[selected="selected"]`)[0]
                    currently_selected_option.removeAttribute("selected")
                //the finally insert the selection in the newly selected option
                    select_item.value=result.division_id // we select the option
                    selected_option=select_item.options[select_item.selectedIndex] // after option is selected, we insert 'selected'
                    selected_option.setAttribute('selected','selected')
        // Division via
            //Span
                document.getElementById(`span_division_via_${contract_id}`).innerHTML="searched_value:"+result.division_via_id
            //Select
                var select_item= document.getElementById(`division_via_${contract_id}`)
                //we first need to remove the selected from the previous option ( otherwise it remains)
                    currently_selected_option=select_item.querySelectorAll(`option[selected="selected"]`)[0]
                    currently_selected_option.removeAttribute("selected")
                //the finally insert the selection in the newly selected option
                    select_item.value=result.division_via_id // we select the option
                    selected_option=select_item.options[select_item.selectedIndex] // after option is selected, we insert 'selected'
                    selected_option.setAttribute('selected','selected')
                  
        // Periodicity
            //Span
                document.getElementById(`span_payment_periodicity_${contract_id}`).innerHTML="searched_value:"+result.payment_periodicity_name
            //Select
                    var select_item= document.getElementById(`payment_periodicity_${contract_id}`)
                //we first need to remove the selected from the previous option ( otherwise it remains)
                    currently_selected_option=select_item.querySelectorAll(`option[selected="selected"]`)[0]
                    currently_selected_option.removeAttribute("selected")
                //the finally insert the selection in the newly selected option
                    select_item.value=result.payment_periodicity_id // we select the option
                    selected_option=select_item.options[select_item.selectedIndex] // after option is selected, we insert 'selected'
                    selected_option.setAttribute('selected','selected') 
        // payment_terms
            //Span
                document.getElementById(`span_payment_terms_${contract_id}`).innerHTML=result.payment_terms
            //output
                document.getElementById(`payment_terms_${contract_id}`).setAttribute("value",`${result.payment_terms}`)
        // Brand
            //Span
                document.getElementById(`span_m3_brand_${contract_id}`).innerHTML="searched_value:"+result.m3_brand_name
            //Select
                    var select_item= document.getElementById(`m3_brand_${contract_id}`)
                //we first need to remove the selected from the previous option ( otherwise it remains)
                    currently_selected_option=select_item.querySelectorAll(`option[selected="selected"]`)[0]
                    currently_selected_option.removeAttribute("selected")
                //the finally insert the selection in the newly selected option
                    select_item.value=result.m3_brand_id // we select the option
                    selected_option=select_item.options[select_item.selectedIndex] // after option is selected, we insert 'selected'
                    selected_option.setAttribute('selected','selected') 
        // mini_gar_status
            //Span
                document.getElementById(`span_mini_gar_status_${contract_id}`).innerHTML="searched_value:"+result.mini_gar_status
            //Select    
                    var select_item= document.getElementById(`mini_gar_status_${contract_id}`)
                //we first need to remove the selected from the previous option ( otherwise it remains)
                    currently_selected_option=select_item.querySelectorAll(`option[selected="selected"]`)[0]
                    currently_selected_option.removeAttribute("selected")
                //the finally insert the selection in the newly selected option
                    select_item.value=result.mini_gar_status // we select the option
                    selected_option=select_item.options[select_item.selectedIndex] // after option is selected, we insert 'selected'
                    selected_option.setAttribute('selected','selected')

        // minimum_guar_amount
            //Span
                document.getElementById(`span_minimum_guar_amount_${contract_id}`).innerHTML=result.minimum_guar_amount
            //output
                document.getElementById(`minimum_guar_amount_${contract_id}`).setAttribute("value",result.minimum_guar_amount.toString().replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1,'))
        // country mini gar
            //Span
                document.getElementById(`span_minimum_guar_remaining_allocation_country_${contract_id}`).innerHTML="searched_value:"+result.country_name
            //Select    
                    var select_item= document.getElementById(`minimum_guar_remaining_allocation_country_${contract_id}`)
                //we first need to remove the selected from the previous option ( otherwise it remains)
                    currently_selected_option=select_item.querySelectorAll(`option[selected="selected"]`)[0]
                    currently_selected_option.removeAttribute("selected")
                //the finally insert the selection in the newly selected option
                    select_item.value=result.country_id // we select the option
                    selected_option=select_item.options[select_item.selectedIndex] // after option is selected, we insert 'selected'
                    selected_option.setAttribute('selected','selected')
        
        //------------------------------------------------------------------------

        //------------------------------------------------------------------------
        //Third, save the modification in the datatable
            var t = $('#contracts_table').DataTable()
            var row_to_modify=document.getElementById(`contract_${contract_id}`)
            td_list=row_to_modify.querySelectorAll("td")
            var td_list_html=[
                td_list[0].innerHTML,
                td_list[1].innerHTML,
                td_list[2].innerHTML,
                td_list[3].innerHTML,
                td_list[4].innerHTML,
                td_list[5].innerHTML,
                td_list[6].innerHTML,
                td_list[7].innerHTML,
                td_list[8].innerHTML,
                td_list[9].innerHTML,
                td_list[10].innerHTML,
                td_list[11].innerHTML,
                td_list[12].innerHTML,
            ]
           t.row(row_to_modify).data(td_list_html).draw(false)
        //------------------------------------------------------------------------
        restate_color_button(contract_id)
        hide_column()              
    })
    //.then(restate_color_button(contract_id))  // we restate the color to blank 
}


function change_row_contract(contract_id,elm){

    unhide_column()
        payment_terms=document.getElementById(`payment_terms_${contract_id}`).value
        if (payment_terms=="") {
            hide_column()
            alert("payment terms cannot be null ")
            return}
        contract_name = document.getElementById(`contract_name_${contract_id}`).value,
        transaction_direction= document.getElementById(`transaction_direction_${contract_id}`).value,
        division_id= document.getElementById(`division_${contract_id}`).value,
        division_via_id= document.getElementById(`division_via_${contract_id}`).value,
        payment_periodicity_id= document.getElementById(`payment_periodicity_${contract_id}`).value,
        brand_id= document.getElementById(`m3_brand_${contract_id}`).value,
        mini_gar_status= document.getElementById(`mini_gar_status_${contract_id}`).value,
        minimum_guar_amount= document.getElementById(`span_minimum_guar_amount_${contract_id}`).innerHTML,
        country_id= document.getElementById(`minimum_guar_remaining_allocation_country_${contract_id}`).value,  
    hide_column()
    fetch(`/change_row_contract/${contract_id}`, {
        method: 'PUT',
        body: JSON.stringify({
            contract_name : contract_name,
            transaction_direction: transaction_direction,
            division_id: division_id,
            division_via_id: division_via_id,
            payment_periodicity_id: payment_periodicity_id,
            payment_terms: payment_terms,
            brand_id: brand_id,
            mini_gar_status: mini_gar_status,
            minimum_guar_amount: minimum_guar_amount,
            country_id: country_id,       
        })
      }).then(response => response.json())
        .then(result => {
            
            changed_row=document.getElementById(`contract_${contract_id}`)
            color_changed_row=changed_row.style.backgroundColor
            changed_row.style.backgroundColor="#b3e3be"
            message_save.hidden=false
            
            setTimeout(function() {message_save.hidden=true; changed_row.style.backgroundColor=color_changed_row }, 1000)
            unhide_column()
            restate_color_button(contract_id)
            hide_column()
            })     
}



function restate_color_button(contract_id){
    document.getElementById(`change_${contract_id}`).hidden=true
    document.getElementById(`cancel_${contract_id}`).hidden=true
    var entire_row = document.getElementById(`contract_${contract_id}`)
    for (var j = 0, col; col = entire_row.cells[j]; j++) {
        col.style.backgroundColor  = "transparent"
      }    
}


function add_new_record(){
    // Here we grab the values from the form
        //Name
            var name_input=document.getElementById("contract_name_new")
            var contract_name= name_input.value
        //transaction_direction
            var transaction_direction_input=document.getElementById("transaction_direction_new")
            var transaction_direction= transaction_direction_input.value
        //division
            var division_input=document.getElementById("displayed_item_name_division_new")
            var division_name=division_input.value
            var division_id= document.getElementById("hidden_item_code_division_new").value
        //division via
            var division_via_input=document.getElementById("displayed_item_name_division_via_new")
            var division_via_name=division_via_input.value
            var division_via_id= document.getElementById("hidden_item_code_division_via_new").value
        //contract currency
            var contract_currency_input=document.getElementById("displayed_item_name_contract_currency_new")
            var contract_currency_name=contract_currency_input.value
            var contract_currency_id= document.getElementById("hidden_item_code_contract_currency_new").value
        //payment periodicity
            var periodicity_input=document.getElementById("displayed_item_name_periodicity_new")
            var periodicity_name=periodicity_input.value
            var periodicity_id= document.getElementById("hidden_item_code_periodicity_new").value
        //payment_terms
            var payment_terms_input=document.getElementById("payment_terms_new")
            var payment_terms= payment_terms_input.value
        //m3_brand
            var m3_brand_input=document.getElementById("displayed_item_name_m3_brand_new")
            var m3_brand_name=m3_brand_input.value
            var brand_id= document.getElementById("hidden_item_code_m3_brand_new").value
        //mini_gar_status
            var mini_gar_status_input=document.getElementById("mini_gar_status_new")
            var mini_gar_status= mini_gar_status_input.value 
        //minimum_guar_amount
            var minimum_guar_amount_input=document.getElementById("minimum_guar_amount_new")
             var minimum_guar_amount_comma=minimum_guar_amount_input.value
            var minimum_guar_amount= minimum_guar_amount_input.value.split(',').join("") // remove comma   
        //minimum_guar_remaining_allocation_country
            var country_input=document.getElementById("displayed_item_name_country_new")
            var country_name=country_input.value
            var country_id= document.getElementById("hidden_item_code_country_new").value
    //create a dictionnary based on the element here above:
        field_dictionnary=[
            {field_name:'contract_name',value:contract_name,object:name_input,mandatory:true},
            {field_name:'transaction_direction',value:transaction_direction,object:transaction_direction_input,mandatory:true},
            {field_name:'division_id',value:division_id,object:division_input,mandatory:true},
            {field_name:'division_via_id',value:division_via_id,object:division_via_input,mandatory:false},
            {field_name:'contract_currency_id',value:contract_currency_id,object:contract_currency_input,mandatory:true},
            {field_name:'periodicity_id',value:periodicity_id,object:periodicity_input,mandatory:true},
            {field_name:'payment_terms',value:payment_terms,object:payment_terms_input,mandatory:true},
            {field_name:'brand_id',value:brand_id,object:m3_brand_input,mandatory:true},
            {field_name:'mini_gar_status',value:mini_gar_status,object:mini_gar_status_input,mandatory:false},
            {field_name:'minimum_guar_amount',value:minimum_guar_amount,object:minimum_guar_amount_input,mandatory:false},
            {field_name:'country_id',value:country_id,object:country_input,mandatory:false},
        ]
        length_dictionnary= field_dictionnary.length  
    //check any of the mandatory field are missing- 
        //filter dictionnary based on mandatory elements + element for which there are no value
        var field_dictionnary_mandatory =  field_dictionnary.filter(d =>d.mandatory==true).filter(d =>d.value=="" );
        // if any of the mandatory field is missing, then we should indicate to the user the missing fiels + stop the function
        var length_mandatory= field_dictionnary_mandatory.length 
        if (length_mandatory>0) {
            message_error.hidden=false
            for (var i = 0; i < length_mandatory; i++) {
                field_dictionnary_mandatory[i]["object"].style.backgroundColor="#f58383"
            } 
            //during 2 secong, we let the error message
            setTimeout(function() { 
                message_error.hidden=true
                for (var i = 0; i < length_mandatory; i++) {
                    field_dictionnary_mandatory[i]["object"].style.backgroundColor=""
                }} , 
                2000)}
        else {
            // we prepare the file to be imported in database
            var import_array = []
            for (var i = 0; i < length_dictionnary; i++) {
                import_array.push(`"${field_dictionnary[i]["field_name"]}":"${field_dictionnary[i]["value"]}"`)
            } 
            import_string="{"+import_array+"}"
            // We load it via a fetch in the API
            fetch('/new_contract', {
                method: 'POST',
                body: import_string
                })
            
            //retreive the contract ID   and create the additional row
            .then(response => response.json())
            .then(result => {
                if (!!result.error) {alert(result.error);return}
                var contract_id=result.contract_id
                unhide_column()
                //creaation of the element in each cell- which will be lowded in the datatable
                if (mini_gar_status =='YES'){yes_value='selected="selected"';no_value=''}else{yes_value='';no_value='selected="selected"'}
                if (transaction_direction =='REC'){rec_value='selected="selected"';pay_value=''}else{rec_value='';pay_value='selected="selected"'}
               
                var t = $('#contracts_table').DataTable().row.add( [
                    // for each tr in the td ( eight elements in total, seperated by a ","), we insert the HTML elements
                    //tr 0  ID
                        `<a href='/contracts/${contract_id}'><span class="fname" contract_id=${contract_id} id="id_${contract_id}" >${contract_id}</span></a>`,
                    //tr 1 Name
                        `<span hidden=true id="span_contract_name_${contract_id}">${contract_name}</span><input type="text" class="fname" contract_id=${contract_id} id=contract_name_${contract_id} placeholder="m3 code" value="${contract_name}">`,
                    //tr 2 Brand
                        `<span hidden=true id="span_m3_brand_${contract_id}">searched_value:${m3_brand_name}</span>`,
                    //tr 3 division
                        `<span hidden=true id="span_division_${contract_id}">searched_value:${division_id}</span>`,
                    //tr 4 division via
                        `<span hidden=true id="span_division_via_${contract_id}">searched_value:${division_via_id}</span>`,
                    //tr 5 transaction_direction
                        `<span hidden=true id="span_transaction_direction_${contract_id}">searched_value:${transaction_direction}</span>
                        <select class="fname" contract_id=${contract_id} id="transaction_direction_${contract_id}">
                            <option value="PAY" ${ pay_value}>PAY</option>
                            <option value="REC" ${ rec_value}>REC</option>
                        </select>
                        `,
                    //tr 6 payment_currency
                        `<span id="span_contract_currency_${contract_id}">${contract_currency_name}</span>`,
                    //tr 7 periodicity
                        `<span hidden=true id="span_payment_periodicity_${contract_id}">searched_value:${periodicity_name}</span>`,
                    //tr 8 payment_terms
                    `
                        <span hidden=true id="span_payment_terms_${contract_id}">${payment_terms}</span>
                        <input type="number" class="fname" contract_id=${contract_id} id=payment_terms_${contract_id} placeholder="m3 code" value="${payment_terms}">
                    `,
                    //tr 9 mini_gar_status
                        `<span hidden=true id="span_mini_gar_status_${contract_id}">searched_value:${mini_gar_status}</span>
                         <select class="fname" contract_id=${contract_id} id="mini_gar_status_${contract_id}">
                            <option value="YES" ${ yes_value}>YES</option>
                            <option value="NO" ${ no_value}>NO</option>
                        </select>
                        `,

                    //tr 10 minimum_guar_amount
                    `
                        <span hidden=true id="span_minimum_guar_amount_${contract_id}">${minimum_guar_amount}</span>
                        <input type="text" class="fname number-separator" contract_id=${contract_id} id=minimum_guar_amount_${contract_id}  value="${minimum_guar_amount_comma}">
                    `,
                    //tr 11 minimum_guar_remaining_allocation_country
                        `<span hidden=true id="span_minimum_guar_remaining_allocation_country_${contract_id}">searched_value:${country_name}</span>`,
                    //tr 12 Button
                    `
                        <button class="btn btn-sm btn-outline-danger" title="delete" name="delete" contract_id=${contract_id} id="delete_${contract_id}" onclick="delete_row_contract('${contract_id}')"><span class="bi bi-trash"></span></button>
                        <button class="btn btn-sm btn-outline-success" title="save modification" contract_id=${contract_id} name="change" id="change_${contract_id}" hidden=true onclick="change_row_contract('${contract_id}')"><span class="bi bi-save2-fill"></span></button>
                        <button class="btn btn-sm btn-outline-warning" title="cancel modification" contract_id=${contract_id} name="cancel" id="cancel_${contract_id}" onclick="cancel_row_contract('${contract_id}')" hidden=true><span class="bi bi-x-circle"></span></button>
                    `,
                ] ).draw( false ).node();
                // a new tr has been created, here add some attribute ( id and contract_id)
                    $(t).attr('contract_id',`${contract_id}`);
                    $(t).attr("id", `contract_${contract_id}`);
                // the last tr, which corresponds to the buttons, must have a class attribute called "button_td"- this is used as a reference for the CSS
                    td_button=t.getElementsByTagName("td")[12];
                    $(td_button).attr('class','button_td');
                                        
                    //for Brand and division, division via, we need to add a drop down- as the dorpdown is pretty long, instead of adding it in the previous section (.draw.node) 
                    //we prefer to copy the lists from a div- those divs are hidden to the user, and contain the country and payment list
                        //........................................Add a Brand drop down list to the newly created row------------------
                            // select and clone the dd
                                var itm = document.getElementById("m3_brand_newlist"); 
                                var cln = itm.cloneNode(true);
                            // we select xth element from this row, which correspond to the column
                                selected_td=t.getElementsByTagName("td")[2]; 
                            //// we append the drop down list
                                selected_td.appendChild(cln)
                            // we select the last node in the td (the first node being the span) and change the ID and contract code
                                $(selected_td.lastChild).attr('contract_id',`${contract_id}`); 
                                $(selected_td.lastChild).attr('id',`m3_brand_${contract_id}`);
                            // we select from the list, the option node with the same country ID as the one entered by the user + we select it
                                td_to_select=selected_td.querySelectorAll(`option[value="${brand_id}"]`)[0]
                                $(td_to_select).attr('selected',`selected`)
                        //........................................------------------------------------------------------------------

                        //........................................Add a division drop down list to the newly created row------------------
                            // select and clone the dd
                                var itm = document.getElementById("division_newlist"); 
                                var cln = itm.cloneNode(true);
                            // we select xth element from this row, which correspond to the column
                                selected_td=t.getElementsByTagName("td")[3]; 
                            //// we append the drop down list
                                selected_td.appendChild(cln)
                            // we select the last node in the td (the first node being the span) and change the ID and contract code
                                $(selected_td.lastChild).attr('contract_id',`${contract_id}`); 
                                $(selected_td.lastChild).attr('id',`division_${contract_id}`);
                            // we select from the list, the option node with the same country ID as the one entered by the user + we select it
                                td_to_select=selected_td.querySelectorAll(`option[value="${division_id}"]`)[0]
                                $(td_to_select).attr('selected',`selected`)
                        //........................................------------------------------------------------------------------
                        
                        //........................................Add a division via drop down list to the newly created row------------------
                            // select and clone the dd
                                var itm = document.getElementById("division_via_newlist"); 
                                var cln = itm.cloneNode(true);
                            // we select xth element from this row, which correspond to the column
                                selected_td=t.getElementsByTagName("td")[4]; 
                            //// we append the drop down list
                                selected_td.appendChild(cln)
                            // we select the last node in the td (the first node being the span) and change the ID and contract code
                                $(selected_td.lastChild).attr('contract_id',`${contract_id}`); 
                                $(selected_td.lastChild).attr('id',`division_via_${contract_id}`);
                            // we select from the list, the option node with the same country ID as the one entered by the user + we select it
                                td_to_select=selected_td.querySelectorAll(`option[value="${division_via_id}"]`)[0]
                                $(td_to_select).attr('selected',`selected`)
                        //........................................------------------------------------------------------------------

                        //........................................------------------------------------------------------------------
                        //........................................Add a period drop down list to the newly created row------------------
                            // select and clone the dd
                                var itm = document.getElementById("payment_periodicity_newlist"); 
                                var cln = itm.cloneNode(true);
                            // we select xth element from this row, which correspond to the column
                                selected_td=t.getElementsByTagName("td")[7]; 
                            //// we append the drop down list
                                selected_td.appendChild(cln)
                            // we select the last node in the td (the first node being the span) and change the ID and contract code
                                $(selected_td.lastChild).attr('contract_id',`${contract_id}`); 
                                $(selected_td.lastChild).attr('id',`payment_periodicity_${contract_id}`);
                            // we select from the list, the option node with the same country ID as the one entered by the user + we select it
                                td_to_select=selected_td.querySelectorAll(`option[value="${periodicity_id}"]`)[0]
                                $(td_to_select).attr('selected',`selected`)
                        //........................................------------------------------------------------------------------
                        //........................................Add a country  drop down list to the newly created row------------------
                            // select and clone the dd
                                var itm = document.getElementById("country_newlist"); 
                                var cln = itm.cloneNode(true);
                            // we select xth element from this row, which correspond to the column
                                selected_td=t.getElementsByTagName("td")[11]; 
                            //// we append the drop down list
                                selected_td.appendChild(cln)
                            // we select the last node in the td (the first node being the span) and change the ID and contract code
                                $(selected_td.lastChild).attr('contract_id',`${contract_id}`); 
                                $(selected_td.lastChild).attr('id',`minimum_guar_remaining_allocation_country_${contract_id}`);
                            // we select from the list, the option node with the same country ID as the one entered by the user + we select it
                                td_to_select=selected_td.querySelectorAll(`option[value="${country_id}"]`)[0]
                                $(td_to_select).attr('selected',`selected`)
                        //........................................------------------------------------------------------------------
                        
                        //we clear the search items
                            $('#contracts_table').DataTable().search("").columns().search('').draw()
                            table=document.getElementById("contracts_table")
                            search_row=table.children[0].children[0]
                            search_input=search_row.querySelectorAll("input")
                            for (s in search_input){search_input[s].value=""}

                        //message_save=document.getElementById("message_save")

                            tr_newlycreated=document.getElementById(`contract_${contract_id}`)
                            color_tr_newlycreated=tr_newlycreated.style.backgroundColor
                            tr_newlycreated.style.backgroundColor="#b3e3be"
                            message_save.hidden=false
                            setTimeout(function() { message_save.hidden=true;tr_newlycreated.style.backgroundColor=color_tr_newlycreated }, 1000) // we show a text explaining that thje load has been done
                            hide_column()
                            document.getElementById("form_new").reset() // once the form is submitted , we reset the form                
            }) 
        }
       
}


function is_in_tbody(event){
    var e= event.target;
    node=e.parentNode
    while (node != null){
        if (node.id=="tbody_contracts") {return true }else{}
        node = node.parentNode;
    }
    return false   
}

function isadropdownlist(element_id){
    list_column=['m3_brand_','division_','division_via_','transaction_direction_','payment_periodicity_','mini_gar_status_','minimum_guar_remaining_allocation_country_']
    
    for (var j = 0, dd_name; dd_name = list_column[j]; j++) {
        if (element_id.includes(dd_name)) {return true}
    } 
    return false
}

function hide_option(){
    //By default the Min Gar options are hidden
    mini_gar_status=document.getElementById("mini_gar_status_new").value
    mini_gar_option_list=document.querySelectorAll(".mini_gar_option")   
    if (mini_gar_status=="YES"){
       mini_gar_option_list[0].hidden=false
       mini_gar_option_list[1].hidden=false
    }else{
       mini_gar_option_list[0].hidden=true
       mini_gar_option_list[1].hidden=true
    }
}

function cancel_new_record(){
    // when clicking on cancel the form, we must hide the option button
    mini_gar_status=document.getElementById("mini_gar_status_new").value
    mini_gar_option_list=document.querySelectorAll(".mini_gar_option")   
    mini_gar_option_list[0].hidden=true
    mini_gar_option_list[1].hidden=true
}

function column_sel(){

    column_selection=document.getElementById("column_selection")
    if (column_selection.style.display == "none"){
        column_selection.style.display="block"}
        else{column_selection.style.display="none"}
}

function column_visibility(elm,column_nb){
    var table = $('#contracts_table').DataTable();
    if (elm.checked){
        table.column( column_nb ).visible( true );
    }else{
        table.column( column_nb ).visible( false );
    }

}

function unhide_column(){
    var table = $('#contracts_table').DataTable();
    table.columns().visible( true );
}

function hide_column(){
    column_selection=document.getElementById("column_selection")
    var table = $('#contracts_table').DataTable();
    uncheck_list=column_selection.querySelectorAll('input[type="checkbox"]:not(:checked)')
    for (c = 0; c < uncheck_list.length; c++){
        column_nb=uncheck_list[c].value
        table.column( column_nb ).visible( false );
    }
}