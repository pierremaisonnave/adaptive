


document.addEventListener('DOMContentLoaded', function() {

    //--------------------Initialization of Datatable ---------------------
    //the datatable is imported, and ordered
    $('#partners_table').DataTable({
        "aaSorting": [[ 0, "desc" ]],
        columnDefs: [{ orderable: false, targets: [0,1,2,3,4,5,6,7] }],
        })


    //the datatable automatically generate a filter button, we do not need it ( as we have search bar for each column)
    document.getElementById("partners_table_filter").hidden=true
    var table = $('#partners_table').DataTable();

    // when we select a search item, the following element must take place
    $('.fname2').on( 'keyup', function () {
        var column_nb=this.getAttribute("column")
        if (['3','4','6'].includes(column_nb)) {searched_value=`searched_value:${this.value}`} else {searched_value=this.value}
        table
            .columns( column_nb )
            .search( searched_value  )
            .draw();
        } 
    );
    //----------------------------------------------------------------------   
  
    // event to be taken when an object in the table is modified:
    document.addEventListener('change', event => {
        
        if (is_in_tbody(event)==false) { return;} //everytime smt is modifyied in the Tbody, we should do the below element, otherwise we do nothing

        //the change and cancel button at the end of the list should be made visible + the background of the cell should be yellowed
        element= event.target
        var partner_id = element.getAttribute("partner_id") 
        document.getElementById(`change_${partner_id}`).hidden=false
        document.getElementById(`cancel_${partner_id}`).hidden=false
        element.parentElement.style.backgroundColor  = "#f2dfa1"

    //When the user modiy the input box , or the dropdown, we also need to update the hidden span located in the same cell- indeed, the search box at the top of each column look for the value in the span, not in the input
        //Country
        span_element=document.getElementById("span_"+element.id)

        if (element.id.includes("country_")){
            //we first need to remove the selected from the previous option ( otherwise it remains)- for a reason I cannot explain, even though the user has selected a different country, the HTML do not show the "Selected"
            currently_selected_option=element.querySelectorAll(`option[selected="selected"]`)[0]
            currently_selected_option.removeAttribute("selected")

            // We get the text value of the selected option
            selected_option=element.options[element.selectedIndex]
            country_name=selected_option.value // the option in the dd is made of the country-Code and the country name, separated by a ":"- We must select the country name ( 2nd, hence[1])
            // then we paste it in the hidden span- The searched box loop through the table, and filter based on whether the searched item is in the cell. As the drop down box, has all the countries, no matter what we enter in the search bar, the row will be hidden-
            // the trick consit on searching based on "searched_value:+country_name " ( see JS " $('.fname2').on( 'keyup', function ()" here above)
            span_element.innerHTML="searched_value:"+country_name 
            selected_option.setAttribute('selected','selected')
        }
        //payment type- aproach similar to country
        else if (element.id.includes("payment_type_")) {
            currently_selected_option=element.querySelectorAll(`option[selected="selected"]`)[0]
            currently_selected_option.removeAttribute("selected")

            selected_option=element.options[element.selectedIndex]
            value_option=element.options[element.selectedIndex].text
            span_element.innerHTML="searched_value:"+value_option
            selected_option.setAttribute('selected','selected')
        }
        else if (element.id.includes("ico_3rd_")) {
            currently_selected_option=element.querySelectorAll(`option[selected="selected"]`)[0]
            currently_selected_option.removeAttribute("selected")
            selected_option=element.options[element.selectedIndex]
            value_option=element.options[element.selectedIndex].text
            span_element.innerHTML="searched_value:"+value_option
            selected_option.setAttribute('selected','selected')
        }
        //the others (  M3 Code, Name)
        else {
            span_element.innerHTML=element.value
            $(element).attr('value',element.value)
        }
        //once the modification has been done in the DOM ( here above) we also must do the modif in the Datatable ( so that we can apply filter and other JQuery)   
        modification_=element.parentElement.innerHTML//
        var t = $('#partners_table').DataTable() 
        t.cell(element.parentElement).data(modification_).draw(false)

    })

})





function delete_row(partner_id) {
    var t = $('#partners_table').DataTable()
    var r = confirm("Are you sure!");
    if (r == true) {
        fetch(`/delete_row_partner/${partner_id}`, {
            method: 'POST',})
        .then(response => response.json())
        .then(result => {
            if (result.error){
                alert(result.error)
            }else{
                tr_to_delete=document.getElementById(`partner_${partner_id}`) 
                t.row( tr_to_delete ).remove().draw(false);
            }
        })
    } 
}

function cancel_row_partner(partner_id){
    //Everytime the user decide to cancel a modification, we must go thought a 3 steps approache
    //firts, we must get the original info from the database, through a fetch, Second, we modify the DOM, Thirds we load it in the Database
    fetch(`/cancel_row_partner/${partner_id}`)
    //First, get the info from database
    .then(response => response.json())
    .then(result => {
    
    //------------------------------------------------------------------------
        //Second, populate the page based on the info extracted from the databse
        //we first need to unhide all columns
        unhide_column()
        //M3 Code
            document.getElementById(`span_m3_code_${partner_id}`).innerHTML=result.partner_m3_code
            document.getElementById(`m3_code_${partner_id}`).setAttribute("value",`${result.partner_m3_code}`)
        // Name
            document.getElementById(`span_name_${partner_id}`).innerHTML=result.partner_name
            document.getElementById(`name_${partner_id}`).setAttribute("value",`${result.partner_name}`)
        // Ico_3rd
            //Span
                document.getElementById(`span_ico_3rd_${partner_id}`).innerHTML="searched_value:"+result.ico_3rd
            //Select
                var ico_3rd_list= document.getElementById(`ico_3rd_${partner_id}`)
                //we first need to remove the selected from the previous option ( otherwise it remains)
                currently_selected_option=ico_3rd_list.querySelectorAll(`option[selected="selected"]`)[0]
                currently_selected_option.removeAttribute("selected")
                //the finally insert the selection in the newly selected item
                ico_3rd_list.value=result.ico_3rd // we select the item
                selected_option=ico_3rd_list.options[ico_3rd_list.selectedIndex] // after item is selected, we insert 'selected'
                selected_option.setAttribute('selected','selected')
        // Country
            //Span
                document.getElementById(`span_country_${partner_id}`).innerHTML="searched_value:"+result.country_id
            //Select
                var country_list= document.getElementById(`country_${partner_id}`)
                //we first need to remove the selected from the previous option ( otherwise it remains)
                currently_selected_option=country_list.querySelectorAll(`option[selected="selected"]`)[0]
                currently_selected_option.removeAttribute("selected")
                //the finally insert the selection in the newly selected countr
                country_list.value=result.country_id // we select the country
                selected_option=country_list.options[country_list.selectedIndex] // after country is selected, we insert 'selected'
                selected_option.setAttribute('selected','selected')

        // bank account
            document.getElementById(`span_bank_${partner_id}`).innerHTML="searched_value:"+result.partner_bank_account
            document.getElementById(`bank_${partner_id}`).setAttribute("value",`${result.partner_bank_account}`) 
        //payment type   
            //span   
                document.getElementById(`span_payment_type_${partner_id}`).innerHTML=result.partner_payment_type
            //Select
                var payment_list= document.getElementById(`payment_type_${partner_id}`)
                //we first need to remove the selected from the previous option ( otherwise it remains)
                currently_selected_option=payment_list.querySelectorAll(`option[selected="selected"]`)[0]
                currently_selected_option.removeAttribute("selected")
                //the finally insert the selection in the newly selected countr
                payment_list.value=result.partner_payment_type_id // we select the country
                selected_option=payment_list.options[payment_list.selectedIndex] // after country is selected, we insert 'selected'
                selected_option.setAttribute('selected','selected')
        //------------------------------------------------------------------------

        //------------------------------------------------------------------------
        //Third, save the modification in the datatable
            var t = $('#partners_table').DataTable()
            var row_to_modify=document.getElementById(`partner_${partner_id}`)
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
            ]
            t.row(row_to_modify).data(td_list_html).draw(false)

        //------------------------------------------------------------------------

        restate_color_button(partner_id)         // we restate the color to blank   
        hide_column()   
    }); 
}


function change_row(partner_id){
    unhide_column()
    partner_m3_code = document.getElementById(`m3_code_${partner_id}`).value,
    partner_name = document.getElementById(`name_${partner_id}`).value,
    ico_3rd = document.getElementById(`ico_3rd_${partner_id}`).value,
    country_id =document.getElementById(`country_${partner_id}`).value,
    partner_bank_account =document.getElementById(`bank_${partner_id}`).value,   
    partner_payment_type_id  =document.getElementById(`payment_type_${partner_id}`).value, 
    hide_column()     
    fetch(`/change_row/${partner_id}`, {
        
        method: 'PUT',
        body: JSON.stringify({
            partner_m3_code : partner_m3_code,
            partner_name : partner_name,
            ico_3rd : ico_3rd,
            country_id :country_id,
            partner_bank_account :partner_bank_account,   
            partner_payment_type_id  :partner_payment_type_id,       
        })
      }).then(response => response.json())
        .then(result => {
            tr_newlycreated=document.getElementById(`partner_${partner_id}`)
            color_tr_newlycreated=tr_newlycreated.style.backgroundColor
            tr_newlycreated.style.backgroundColor="#b3e3be"
            message_save.hidden=false

            setTimeout(function() { message_save.hidden=true;tr_newlycreated.style.backgroundColor=color_tr_newlycreated }, 1000) // we show a text explaining that thje load has been done
            unhide_column()
            restate_color_button(partner_id)
            hide_column()
            })
       
}



function restate_color_button(partner_id){
    if (document.getElementById(`change_${partner_id}`)){
    document.getElementById(`change_${partner_id}`).hidden=true
    document.getElementById(`cancel_${partner_id}`).hidden=true
    var entire_row = document.getElementById(`partner_${partner_id}`)
    for (var j = 0, col; col = entire_row.cells[j]; j++) {
        col.style.backgroundColor  = "transparent"
      }  
    }  
}


function add_new_record(){
    // Here we grab the values from the form
        //M3 Code
            var m3_input=document.getElementById("partner_m3_code_new")
            var partner_m3_code= m3_input.value
        //Name
            var name_input=document.getElementById("name_new")
            var partner_name= name_input.value
        //ico_3rd
            var new_ico_3rd=document.getElementById("new_ico_3rd")
            var ico_3rd= new_ico_3rd.value
      
        //country
            var country_input=document.getElementById("displayed_item_name_new_country")
            var country_id= document.getElementById("hidden_item_code_new_country").value
            var country_name=country_input.value
        //Bank
            var partner_bank_account= document.getElementById("bank_new").value
        //payment
            var payment_input=document.getElementById("displayed_item_name_new_payment")
            var payment_id= document.getElementById("hidden_item_code_new_payment").value
            var payment_name=payment_input.value    
    
    //check if Name, Country, Payment Type are missing- if so, show an error message for 2 second, + a red round over the incorrect input
        
        if ([partner_m3_code, partner_name ,country_name,payment_name].includes("") ) {
            message_error.hidden=false

            if (partner_m3_code ==""){m3_input.style.backgroundColor="#f58383"}
            if (partner_name ==""){name_input.style.backgroundColor="#f58383"}
            if (country_name ==""){country_input.style.backgroundColor="#f58383"}
            if (payment_name ==""){payment_input.style.backgroundColor="#f58383"}

            setTimeout(function() { 
                message_error.hidden=true;
                m3_input.style.backgroundColor =""
                name_input.style.backgroundColor=""
                country_input.style.backgroundColor=""
                payment_input.style.backgroundColor=""
            }, 
            2000)
        }
        else {
            //define spinner
            spinner=document.getElementById("spinner")
            saved_button=document.getElementById(id="saved_button")
            saved_message=document.getElementById(id="saved_message")
            spinner.style.display = "Block"
            saved_button.style.display = "None"
            // We load it via a fetch in the API
            fetch('/new_partner', {
                method: 'POST',
                body: JSON.stringify({
                    partner_m3_code:partner_m3_code,
                    partner_name:partner_name,
                    ico_3rd:ico_3rd,
                    country_id:country_id,
                    partner_bank_account:partner_bank_account,
                    partner_payment_type_id:payment_id,
                    })
                })
            //retreive the partner ID  (result.partner_id ) and create the additional row
                .then(response => response.json())
                .then(result => {
                    if (!!result.error) {alert(result.error);return}
                    var partner_id=result.partner_id
                    unhide_column()
                    // we prepare the select option for ico_3rd
                        if (ico_3rd=="ICO"){ico_select='selected="selected"'; third_select=""}else{ico_select="";third_select='selected="selected"'}
                    //creaation of the element in each cell- which will be lowded in the datatable
                    var t = $('#partners_table').DataTable().row.add( [
                        // for each tr in the td ( eight elements in total, seperated by a ","), we insert the HTML elements
                        //tr 0  ID
                        `<span class="fname" partner_id=${partner_id} id="id_${partner_id}" >${partner_id}</span>`,
                        //tr 1 M3 Code
                        `
                            <span hidden=true id="span_m3_code_${partner_id}">${partner_m3_code}</span>
                            <input type="text" class="fname" partner_id=${partner_id} id=m3_code_${partner_id} placeholder="m3 code" value="${partner_m3_code}">
                        `,
                        //tr 2 Name
                        `
                            <span hidden=true id="span_name_${partner_id}">${partner_name}</span>
                            <input type="text" class="fname" partner_id=${partner_id} id="name_${partner_id}" placeholder="name" value='${partner_name}'>
                        `,
                        //tr 3 ico_3rd
                        `
                            <span hidden=true id="span_ico_3rd_${partner_id}">searched_value:${ico_3rd}</span>
                            <select style="width:100%;background-color: transparent;border-style: hidden;" partner_id=${partner_id} id="ico_3rd_${partner_id}">
                                <option value="3rd" ${third_select}>3rd</option>
                                <option value="ICO" ${ico_select}>ICO</option>
                            </select>
                        `,
                        //tr 4 Country
                        `<span hidden=true id="span_country_${partner_id}">searched_value:${country_id}</span>`,
                        //tr 5 Bank
                        `
                            <span hidden=true id="span_bank_${partner_id}">${partner_bank_account}</span>
                            <input type="text" class="fname" partner_id=${partner_id} id="bank_${partner_id}" placeholder="bank account here" value='${partner_bank_account}'>
                        `,
                        //tr 6 Payment Type
                        `<span hidden=true id="span_payment_type_${partner_id}">${payment_name}</span>`,
                        //tr 7 Button
                        `
                            <button class="btn btn-sm btn-outline-danger" title="delete" name="delete" partner_id=${partner_id} id="delete_${partner_id}" onclick="delete_row('${partner_id}')"><span class="bi bi-trash"></span></button>
                            <button class="btn btn-sm btn-outline-success" title="save modification" partner_id=${partner_id} name="change" id="change_${partner_id}" hidden=true onclick="change_row('${partner_id}')"><span class="bi bi-save2-fill"></span></button>
                            <button class="btn btn-sm btn-outline-warning" title="cancel modification" partner_id=${partner_id} name="cancel" id="cancel_${partner_id}" onclick="cancel_row_partner('${partner_id}')" hidden=true><span class="bi bi-x-circle"></span></button>
                        `,
                    ] ).draw( false ).node();

                    // a new tr has been created, here add some attribute ( id and partner_id)
                    $(t).attr('partner_id',`${partner_id}`);
                    $(t).attr("id", `partner_${partner_id}`);
                    // the last tr, which corresponds to the buttons, must have a class attribute called "button_td"- this is used as a reference for the CSS
                    td_button=t.getElementsByTagName("td")[7];
                    $(td_button).attr('class','button_td');
                    
                    //for Country and payment, we need to add a drop down- as the dorpdown is pretty long, instead of adding it in the previous section (.draw.node) 
                    //we prefer to copy the lists from a div- those divs are hidden to the user, and contain the country and payment list
                        //........................................Add a country drop down list to the newly created row------------------
                            // there is a div, in this page, that contains the country list- here we copy this div
                                var itm = document.getElementById("country_newlist"); 
                                var cln = itm.cloneNode(true);
                            // we select the 4rth ( which is [4] as 0 is counted) element from this row, which correspond to the the country td
                                td_country_list=t.getElementsByTagName("td")[4]; 
                            //// we append the drop down list
                                td_country_list.appendChild(cln)
                            // we select the last node in the td (the first node being the span) and change the ID and partner code
                                $(td_country_list.lastChild).attr('partner_id',`${partner_id}`); 
                                $(td_country_list.lastChild).attr('id',`country_${partner_id}`);
                            // we select from the list, the option node with the same country ID as the one entered by the user + we select it
                                td_to_select=td_country_list.querySelectorAll(`option[value="${country_id}"]`)[0]
                                $(td_to_select).attr('selected',`selected`)
                        //........................................------------------------------------------------------------------

                        //........................................Add a payment type drop down list to the newly created row------------------
                            // there is a div, in this page, that contains the payment list- here we copy this div
                                var itm = document.getElementById("payment_type_newlist"); 
                                var cln = itm.cloneNode(true);
                            // we select the 6th ( which is [7] as 0 is counted) element from this row, which correspond to the the payment td
                                td_payment_list=t.getElementsByTagName("td")[6]; 
                            //// we append the drop down list
                                td_payment_list.appendChild(cln)
                            // we select the last node in the td (the first node being the span) and change the ID and partner code
                                $(td_payment_list.lastChild).attr('partner_id',`${partner_id}`); 
                                $(td_payment_list.lastChild).attr('id',`payment_type_${partner_id}`);
                            // we select from the list, the option node with the same country ID as the one entered by the user + we select it
                                td_to_select=td_payment_list.querySelectorAll(`option[value="${payment_id}"]`)[0]
                                $(td_to_select).attr('selected',`selected`)
                        //........................................------------------------------------------------------------------
                        
                        //we clear the search items
                             $('#partners_table').DataTable().search("").columns().search('').draw()
                            table=document.getElementById("partners_table")
                            search_row=table.children[0].children[0]
                            search_input=search_row.querySelectorAll("input")
                            for (s in search_input){search_input[s].value=""}

                        //message_save
                        tr_newlycreated=document.getElementById(`partner_${partner_id}`)
                        color_tr_newlycreated=tr_newlycreated.style.backgroundColor
                        tr_newlycreated.style.backgroundColor="#b3e3be"

                        spinner.style.display = "None"
                        saved_message.style.display = "Block";
                        setTimeout(function() { 

                            saved_message.style.display = "None";
                            saved_button.style.display = "Block";
                            tr_newlycreated.style.backgroundColor=color_tr_newlycreated 
                            }, 1000) // we show a text explaining that thje load has been done
                        hide_column()
                        document.getElementById("form_new").reset() // once the form is submitted , we reset the form
                }) 
            }

       
}


function is_in_tbody(event){
    var e= event.target;
    node=e.parentNode
    while (node != null){
        if (node.id=="tbody_partner") {return true }else{}
        node = node.parentNode;
    }
    return false   
}

function column_sel(){
    column_selection=document.getElementById("column_selection")
    if (column_selection.style.display == "none"){
        column_selection.style.display="block"}
        else{column_selection.style.display="none"}
}

function column_visibility(elm,column_nb){
    var table = $('#partners_table').DataTable();
    if (elm.checked){
        table.column( column_nb ).visible( true );
    }else{
        table.column( column_nb ).visible( false );
    }

}

function unhide_column(){
    var table = $('#partners_table').DataTable();
    table.columns().visible( true );
}

function hide_column(){
    column_selection=document.getElementById("column_selection")
    var table = $('#partners_table').DataTable();
    uncheck_list=column_selection.querySelectorAll('input[type="checkbox"]:not(:checked)')
    for (c = 0; c < uncheck_list.length; c++){
        column_nb=uncheck_list[c].value
        table.column( column_nb ).visible( false );
    }
}