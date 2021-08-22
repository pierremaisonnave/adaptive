document.addEventListener('DOMContentLoaded', function() {

    //--------------------Initialization of Datatable ---------------------
    //the datatable is imported, and ordered
    $('#file_table').DataTable({
        "aaSorting": [[ 1, "desc" ]],
        columnDefs: [{ orderable: false, targets: [0,1,2,3,4] }],
        })
    

    //the datatable automatically generate a filter button, we do not need it ( as we have search bar for each column)
    document.getElementById("file_table_filter").hidden=true
    var table = $('#file_table').DataTable();

    // when we select a search item, the following element must take place
    $('.fname2').on( 'keyup', function () {
        var column_nb=this.getAttribute("column")
        table
            .columns( column_nb )
            .search( this.value  )
            .draw()
        } 
        
    );
    period_message()
    //-
})



function add_new_record(){
    event.preventDefault(); // prevent the page from reloading
    //check we are still connected:
        fetch('/isauthenticated', {method: 'GET'})
        .then(response => response.json())
        .then(feedback => {
            if (feedback.isauthenticated=="NO"){document.location.reload()}
        })
    //definition od the elements
    name_=document.getElementById("name_")
    name_value=name_.value

    file_=document.getElementById("fileSelect")
    file_value=file_.value

    year_from_=document.getElementById("year_from")
    year_from=year_from_.value

    year_to_=document.getElementById("year_to")
    year_to=year_to_.value

    month_to_=document.getElementById("month_to")
    month_to=month_to_.value

    //message
    field_dictionnary=[
        {field_name:'name',value:name_value,object:name_,mandatory:true},
        {field_name:'file',value:file_value,object:file_,mandatory:true},
    ] 
    var field_dictionnary_mandatory =  field_dictionnary.filter(d =>d.mandatory==true).filter(d =>d.value=="" );
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
            1000)
    }else{
        //definition of spinner
            message_wait=document.getElementById("message_wait")
            spinner_on()
            message_wait.hidden=false

        let formData = new FormData();
        formData.append('name', name_value);
        formData.append('year_from', year_from);
        formData.append('year_to', year_to);
        formData.append('month_to', month_to);
        formData.append('file_type', 'cash_forecast');
        formData.append('file', file_.files[0], file_.files[0].name);

        //book in database
        fetch('/new_report', {
            method: 'POST',
            body: formData//JSON.stringify({name:name_value,acc_year:year_value,acc_month:month_id,})
            })
        //retreive the partner ID  (result.partner_id ) and create the additional row
            .then(response => response.json())
            .then(result => {
                var file_id=result.file_id
                if (result.error){
                    alert(result.error)
                }else{
                    const timeElapsed = Date.now();
                    const today = new Date(timeElapsed);
                    var time_=today.toDateString() +", "+ today.toLocaleTimeString()
                    //Creation new line
                    var t = $('#file_table').DataTable().row.add( [
                        `<input type="checkbox" class="file_checkbox_list">`,
                        `${file_id}`,
                        `${name_value}`,
                        `${time_}`,
                        `<button class="btn btn-sm btn-outline-danger button_sp" title="delete" name="delete"  onclick="delete_row(this)"><span class="bi bi-trash"></span></button>`,
                    ]).draw( false ).node();
                    //success message
                        initial_gb_color=t.style.backgroundColor
                        t.style.backgroundColor="#b3e3be"
                        
                        message_save=document.getElementById(id="message_save")
                        message_wait.hidden=true
                        message_save.hidden=false
                        setTimeout(function() {
                            message_save.hidden=true;
                            spinner_off()
                            t.style.backgroundColor=initial_gb_color
                        },
                        1000)
                    //reset for:
                        document.getElementById("form_new").reset()
                }
                document.getElementById("form_new").reset()
                message_wait.hidden=true    
            })
    } 
}

function delete_row(elm){
    var t = $('#file_table').DataTable()
    var r = confirm("Are you sure!");
    if (r == true) {
        tr_to_delete=elm.parentElement.parentElement
        file_id=tr_to_delete.children[1].innerHTML
        smooth_remove_row(tr_to_delete,t)
        fetch(`/delete_row_file/${file_id}`, {
            method: 'POST',})
        .then(response => response.json())
        .then(result => {})
    }
}

function export_file(){
    selection_table=document.getElementById("selection_table")
    table_list=selection_table.parentElement.querySelectorAll('input:checked')
    file_table=document.getElementById("file_table")
    file_list=file_table.parentElement.querySelectorAll('input:checked')

    table_list_length=table_list.length
    file_list_length=file_list.length

    if (table_list_length==0 || file_list_length==0 ){
        alert( "please select at least on type of data and one file")
        return
    }else{
        //create list of file
        file_array=[]
        for (i = 0; i < file_list_length; ++i) {
            file_id=file_list[i].parentElement.parentElement.children[1].innerHTML
            file_array.push(file_id)
        }
        file_list_string=JSON.stringify(file_array)


        //create list of table
        table_array=[]
        for (i = 0; i < table_list_length; ++i) {
            file_id=table_list[i].value
            table_array.push(file_id)
        }
        table_list_string=JSON.stringify(table_array)
        window.location.replace(`/export_report/files:${file_array}/tables:${table_array}`)
    }
}

function changeyear(elm){
    if ( elm.id=="year_from" && (year_from.value=="" || year_from.value>year_to.value)){
        alert("cannot be empty or more than year_to")
        year_from.value=year_to.value}
    else{
        period_message()
    }
    if ( elm.id=="year_to" && ( year_to.value=="" || year_from.value>year_to.value)){
        alert("cannot be empty or less than year_from")
        year_to.value=year_from.value}
    else{
        period_message()
    }
}

function period_message(){
    
    if ( message_save.hidden && message_error.hidden && message_wait.hidden ){
        month_to=document.getElementById("month_to")
        year_from=document.getElementById("year_from").value
        year_to=document.getElementById("year_to").value
        month_to=month_to.options[month_to.selectedIndex].text
        period_message_date=document.getElementById("period_message_date")
        period_message_date.innerHTML=`from January ${year_from} to ${month_to} ${year_to}`
        message_period.hidden=false
    }
    else{

    }
}