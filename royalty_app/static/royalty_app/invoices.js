document.addEventListener('DOMContentLoaded', function() {

    //--------------------Initialization of Datatable ---------------------
    //the datatable is imported, and ordered
    $('#invoices_table').DataTable({
        "aaSorting": [[ 0, "desc" ]],
        columnDefs: [{ orderable: false, targets: [0,1,2,3,4,5,6,7,8] }],
    })

    document.querySelector("main").style.visibility = "visible";
    //the datatable automatically generate a filter button, we do not need it ( as we have search bar for each column)
    document.getElementById("invoices_table_filter").hidden=true
    var table = $('#invoices_table').DataTable();

    // when we select a search item, the following element must take place
    $('.fname2').on( 'keyup', function () {
        var column_nb=this.getAttribute("column")
        table
            .columns( column_nb )
            .search( this.value  )
            .draw();
        } 
    );
})

function onchange_contract(elm){
    
    form=document.getElementById("form_new")
    contract_id=elm.value
    periodicity_id=elm.options[elm.selectedIndex].getAttribute("periodicity_id")


    //enable each item
    disabled_objects=form.querySelectorAll('[disabled="true"]')
    
    if (disabled_objects){
        disabled_objects.forEach(obj=>obj.removeAttribute("disabled"))
    }

    selected_objects=form.querySelectorAll(`option[selected]`)
    if (selected_objects){
        selected_objects.forEach(sel=>sel.removeAttribute("selected"))
    }
    //partner
        //loop through the option, if contract_of_cpid is the same as the contract entered by the user, then we unhide- otherwhise we hide
        //In case we Hide, the first item must be automatically selected
        cp_list=form.querySelectorAll('[contract_of_cp_id]')
        n=0
        cp_list.forEach(cp=>{
            if (cp.getAttribute("contract_of_cp_id")==contract_id){
                cp.hidden=false
                if (n==0){cp.setAttribute('selected','selected')}
                n++
                }else{cp.hidden=true}
        })
        if (n==0){
            alert("please insert some partners for this contract")
            window.location.replace(`/contracts/${contract_id}`)
            }
    // transaction_direction
        transaction_direction=elm.options[elm.selectedIndex].getAttribute("transaction_direction")
        document.getElementById("transaction_direction_").innerHTML=transaction_direction+':'
    // year
        document.getElementById("year_").value=new Date().getFullYear()-1
    //periodicity- same logic as above
        ps_list=form.querySelectorAll('[periodicity_of_ps_id]')
        n=0
        ps_list.forEach(ps=>{
            if (ps.getAttribute("periodicity_of_ps_id")==periodicity_id){
                ps.hidden=false
                if (n==0){ps.setAttribute('selected','selected')}
                n++
                }else{ps.hidden=true}
        })
    // currency
        currency_id=elm.options[elm.selectedIndex].getAttribute("currency")
        document.getElementById("currency_contract_").innerHTML=currency_id

}

function add_new_record(){
    //definition od the elements
    contract_=document.getElementById("contract_")
    contract_value=contract_.options[contract_.selectedIndex].text
    contract_id=contract_.value

    partner_=document.getElementById("partner_")
    partner_value=partner_.options[partner_.selectedIndex].text
    partner_id=partner_.value

    transaction_direction_=document.getElementById("transaction_direction_")
    transaction_direction_value=transaction_direction_.innerHTML

    amount_=document.getElementById("amount_")
    amount_value=amount_.value
    amount_value_wo_comma=Number(amount_value.split(',').join(""))

    currency_contract_=document.getElementById("currency_contract_")
    currency_contract_value=currency_contract_.innerHTML

    year_=document.getElementById("year_")
    year_value=year_.value

    period_=document.getElementById("period_")
    period_value=period_.options[period_.selectedIndex].text
    period_id=period_.value

    comment_=document.getElementById("comment_")
    comment_value=comment_.value
    //message
    field_dictionnary=[
        {field_name:'year',value:year_value,object:year_,mandatory:true},
        {field_name:'amount',value:amount_value,object:amount_,mandatory:true},
    ]   
    var field_dictionnary_mandatory =  field_dictionnary.filter(d =>d.mandatory==true).filter(d =>d.value=="" );
    var length_mandatory= field_dictionnary_mandatory.length

    if (length_mandatory>0) {
        message_error.hidden=false
        for (var i = 0; i < length_mandatory; i++) {
            field_dictionnary_mandatory[i]["object"].style.backgroundColor="#f58383"
        } 
        //during 1 secong, we let the error message
        setTimeout(function() { 
            message_error.hidden=true
            for (var i = 0; i < length_mandatory; i++) {
                field_dictionnary_mandatory[i]["object"].style.backgroundColor=""
            }} , 
            1000)
    }else{
        //book in database
        fetch('/new_invoice', {
            method: 'POST',
            body: JSON.stringify({
                contract_id:contract_id,
                partner_id:partner_id,
                amount_value:amount_value_wo_comma,
                year_value:year_value,
                period_id:period_id,
                comment_value:comment_value,
                })
            })
        //retreive the partner ID  (result.partner_id ) and create the additional row
            .then(response => response.json())
            .then(result => {
                if (result.error){ 
                    alert(result.error)
                    return;
                    }
                var invoice_id=result.invoice_id
                //Creation new line
                var t = $('#invoices_table').DataTable().row.add( [
                    `${invoice_id}`,
                    `${contract_value}`,
                    `${partner_value}`,
                    `<div style="display:grid;grid-template-columns: 30px 30px auto" >
                        <span style="color:grey">${transaction_direction_value}</span>
                        <span style="color:grey">${currency_contract_value}</span>
                        <span>${amount_value}</span>
                    </div>`,
                    `${year_value}`,
                    `${period_value}`,
                    `${comment_value}`,
                    `<input type="checkbox" onclick="save_paid_status(this)">`,
                    `<button class="btn btn-sm btn-outline-danger button_sp" title="delete" name="delete"  onclick="delete_row(this)"><span class="bi bi-trash"></span></button>`,
                ]).draw( false ).node();
                //success message
                    initial_gb_color=t.style.backgroundColor
                    t.style.backgroundColor="#b3e3be"
                    message_save.hidden=false
                    setTimeout(function() {message_save.hidden=true;t.style.backgroundColor=initial_gb_color},1000)
                //reset for:
                    //document.getElementById("form_new").reset()
            }) 
    }
}

function delete_row(elm){
    var t = $('#invoices_table').DataTable()
    row=elm.parentElement.parentElement
    invoice_id=row.children[0].innerHTML

    fetch(`/delete_row_invoice/${invoice_id}`, {
        method: 'POST',})
     
    t.row( row ).remove().draw(false);
}

function save_paid_status(elm){
    row=elm.parentElement.parentElement
    invoice_id=row.children[0].innerHTML
    paid=elm.checked
    fetch('/save_paid_status', {
        method: 'POST',
        body: JSON.stringify({
            paid:paid,
            invoice_id:invoice_id,
            })
        })

}

function column_sel(){
    column_selection=document.getElementById("column_selection")
    if (column_selection.style.display == "none"){
        column_selection.style.display="block"}
        else{column_selection.style.display="none"}
}

function column_visibility(elm,column_nb){
    var table = $('#invoices_table').DataTable();
    if (elm.checked){
        table.column( column_nb ).visible( true );
    }else{
        table.column( column_nb ).visible( false );
    }

}