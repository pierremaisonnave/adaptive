
document.addEventListener('DOMContentLoaded', function() {


    //--------------------Initialization of Datatable ---------------------
    //the datatable is imported, and ordered
    $('#contracts_table').DataTable({
        "aaSorting": [[ 0, "desc" ]],
        //columnDefs: [{ orderable: false, targets: [,12] }],
    })


    //the datatable automatically generate a filter button, we do not need it ( as we have search bar for each column)
    document.getElementById("contracts_table_filter").hidden=true
    var table = $('#contracts_table').DataTable();

    // when we select a search item, the following element must take place
    $('.fname2').on( 'keyup', function () {
        var column_nb=this.getAttribute("column")
          
        table
            .columns( column_nb )
            .search( this.value  )
            .draw();
        } 
    );
    //---------------------Filter-----------------------------------   
    column_selection=document.getElementById("column_selection")
    unchecked_list = column_selection.querySelectorAll('input[type="checkbox"]:not(:checked)')
    for (var j = 0, unchecked_item; unchecked_item = unchecked_list[j]; j++) {
        column_visibility(unchecked_item,unchecked_item.value)
    }
})


function add_new_record(){
    // Here we grab the values from the form
        //Type
            var type_input=document.getElementById("displayed_item_name_type_new")
            var type_name=type_input.value
            var type_id= document.getElementById("hidden_item_code_type_new").value
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

        if (mini_gar_status=="YES"){
            //minimum_guar_amount
                var minimum_guar_amount_input=document.getElementById("minimum_guar_amount_new")
                var minimum_guar_amount_comma=minimum_guar_amount_input.value
                var minimum_guar_amount= minimum_guar_amount_input.value.split(',').join("") // remove comma   
            //minimum_guar_remaining_allocation_country
                var country_input=document.getElementById("displayed_item_name_country_new")
                var country_name=country_input.value
                var country_id= document.getElementById("hidden_item_code_country_new").value
        }else{
            minimum_guar_amount=""
            country_id=""
        }
    //create a dictionnary based on the element here above:
        field_dictionnary=[
            {field_name:'type_id',value:type_id,object:type_input,mandatory:true},
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
            //define spinner
            spinner_contract=document.getElementById("spinner_contract")
            saved_button_contract=document.getElementById(id="saved_button_contract")
            saved_message_contract=document.getElementById(id="saved_message_contract")
            spinner_contract.style.display = "Block"
            saved_button_contract.style.display = "None"
        
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
                        `<a href='/contracts/writer/${contract_id}'><span class="fname" contract_id=${contract_id} id="id_${contract_id}" onclick="spinner()" >${contract_id}</span></a>`,
                    //tr 1 Type
                        `<span >${type_name}</span>`,
                    //tr 2 Name
                        `<span >${contract_name}</span>`,
                    //tr 3 division
                        `<span >${division_id}</span>`,
                    //tr 4 transaction_direction
                        `<span >${transaction_direction}</span>`,
                    //tr 5 payment_currency
                        `<span >${contract_currency_name}</span>`,
                    //tr 6 periodicity
                        `<span >${periodicity_name}</span>`,
                    //tr 7 payment_terms
                        `<span >${payment_terms}</span>
                        `,                    
                    //tr 8 Brand
                        `<span >${m3_brand_name}</span>`,

                    //tr 9 division via
                        `<span >${division_via_id}</span>`,

                    //tr 10 mini_gar_status
                        `<span >${mini_gar_status}</span>`,

                    //tr 11 minimum_guar_amount
                        `<span >${minimum_guar_amount}</span>`,
                    //tr 12 minimum_guar_remaining_allocation_country
                        `<span  >${country_id}</span>`,
                    //tr 13 Button
                    `<span style="color:orange" >IN_CREATION- not submitted yet </span>`,
                ] ).draw( false ).node();
                        
                        //we clear the search items
                            $('#contracts_table').DataTable().search("").columns().search('').draw()
                            table=document.getElementById("contracts_table")
                            search_row=table.children[0].children[0]
                            search_input=search_row.querySelectorAll("input")
                            for (s in search_input){search_input[s].value=""}

                        //message_save=document.getElementById("message_save")

                            color_tr_newlycreated=t.style.backgroundColor
                            t.style.backgroundColor="#b3e3be"
                            saved_message_contract.style.display = "Block"
                            spinner_contract.style.display = "None"
                            
                            setTimeout(function() {
                                saved_message_contract.style.display = "None";
                                saved_button_contract.style.display = "Block";
                                t.style.backgroundColor=color_tr_newlycreated }, 1000) // we show a text explaining that the load has been done
                            hide_column()
                            cancel_new_record()
                            document.getElementById("form_new").reset() // once the form is submitted , we reset the form                
            }) 
        }
       
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

