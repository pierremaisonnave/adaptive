function add_new_row(elm){

    //select the row and table
        new_tr=document.getElementById(id="new_tr")
        main_table=document.getElementById(id="main_table")
    //remove id and onchange action + unhide button
        new_tr.removeAttribute('id');
        elm.removeAttribute('onchange')
        new_tr.children[2].children[0].hidden=false
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

    // column 2 select, clone and insert input
        itm = document.getElementById("column_2").children[0];
        cln = itm.cloneNode(true);
        newCell = newRow.insertCell(2);
        newCell.appendChild(cln)


}

function delete_row(elm){
    tr_to_delete=elm.parentElement.parentElement
    smooth_remove_row_nodatatable(tr_to_delete)
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
        region_id=tr_list[i].children[0].children[0].value
        if (region_id == "" ){region_id=0 } // id is an int, so we need to change all "" value to smth, here we choose 0
        region_name=tr_list[i].children[1].children[0].value
        import_array.push(`{"region_id":"${region_id}","region_name":"${region_name}"}`)
    } 

    import_string="["+import_array+"]"
    // set waiting message:
        saved_message=document.getElementById(id="saved_message")
        //save_button=document.getElementById(id="save_button")
        spinner_on()
        //save_button.style.display="none"
    // We load it via a fetch in the API
    fetch(`/save_region`, {
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
                saved_message.innerHTML="Saved"
                setTimeout(function() { 
                    saved_message.innerHTML="",
                    //save_button.style.display="block"
                    spinner_off()
                    },
                1000)
                location.reload();
            }
        })
}




function is_any_fied_empty(){

    tbody_main_table=document.getElementById(id="tbody_main_table")
    tr_list=tbody_main_table.querySelectorAll("tr")
    length_table=tr_list.length-1

    for (var i = 0; i < length_table; i++) {
        if (tr_list[i].children[1].children[0].value=="" ){
            return true
        }
    } 
    return false
}