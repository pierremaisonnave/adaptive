function add_new_row(elm){
    //check that the value do not already exist
        if (is_unique(elm) ==false){
            alert("this primary key already exist, please choose another one");
            elm.value="" ;
            return}
        elm.setAttribute('previous_value',elm.value) //set a new"previous value" this value will be used to reset the imput in case of wrong typing
    //select the row and table
        new_tr=document.getElementById(id="new_tr")
        main_table=document.getElementById(id="main_table")
    //remove id and onchange action + unhide button
        new_tr.removeAttribute('id');
        elm.removeAttribute('onchange')
        elm.setAttribute('onchange', "is_unique_key(this)") 
        new_tr.children[1].children[0].hidden=false
    //create new row
        var newRow = main_table.insertRow(-1);
        newRow.id="new_tr"

    // column 0 select, clone and insert input
        itm = document.getElementById("column_0").children[0];
        cln = itm.cloneNode(true);
        newCell = newRow.insertCell(0);
        newCell.appendChild(cln)

    // column 1 select, clone and insert Select
        var itm = document.getElementById("column_1").children[0];
        var cln = itm.cloneNode(true);
        newCell = newRow.insertCell(1);
        newCell.appendChild(cln)


}

function delete_row(elm){
    elm.parentNode.parentNode.remove()
}

function save(contract_id){

    //make sure we are not missing any field
    if ( is_any_fied_empty()){alert("make sure all fields are filed in"); return}
    //check if total =100
    tbody_main_table=document.getElementById(id="tbody_main_table")
    tr_list=tbody_main_table.querySelectorAll("tr")
    length_table=tr_list.length-1

    var sum=0
    var import_array = []
    for (var i = 0; i < length_table; i++) {
        payment_type= tr_list[i].children[0].children[0].value
        import_array.push(`{"payment_type":"${payment_type}"}`)
    } 

    import_string="["+import_array+"]"

    // We load it via a fetch in the API
    fetch(`/save_payment_type`, {
        method: 'POST',
        body: import_string
        })
        .then(response => response.json())
        .then(result => {
            if (!!result.error) {
                alert(result.error);
                location.reload();
            }else{
            //message
                saved_message=document.getElementById(id="saved_message")
                saved_message.innerHTML="Saved"
                setTimeout(function() { 
                    saved_message.innerHTML=""},
                1000)
            }
        })
}


function is_unique(elm){
    tbody_main_table=document.getElementById(id="tbody_main_table")
    primary_key_list=tbody_main_table.querySelectorAll('input[primary_key="True"]')
    primary_key_list_length=primary_key_list.length

    n=0
    for (var i = 0; i < primary_key_list_length; i++) {
        if (primary_key_list[i].value == elm.value){
            n++
        }
    }
    if (n!=1){return false} else{return true}   
}
function is_unique_key(elm){
    if (elm.value==""){alert("this value cannot be null"); 
        elm.value=elm.getAttribute("previous_value")
        return}
    if (is_unique(elm) ==false){
        alert("this primary key already exist, please choose another one"); 
        elm.value=elm.getAttribute("previous_value")
        return}else{
        elm.setAttribute("previous_value",elm.value )  
        }
}

function is_any_fied_empty(){

    tbody_main_table=document.getElementById(id="tbody_main_table")
    tr_list=tbody_main_table.querySelectorAll("tr")
    length_table=tr_list.length-1

    for (var i = 0; i < length_table; i++) {
        if (tr_list[i].children[0].children[0].value==""  ){
            return true
        }
    } 
    return false
}