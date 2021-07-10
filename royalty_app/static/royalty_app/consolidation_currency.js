
function save(contract_id){

    //make sure we are not missing any field

    //check if total =100
    tbody_main_table=document.getElementById(id="tbody_main_table")
    tr_list=tbody_main_table.querySelectorAll("tr")
    consolidation_currency= tr_list[0].children[0].children[0].value
    if ( consolidation_currency==""){alert("make sure all fields are filed in"); return}

    import_string=`{"consolidation_currency":"${consolidation_currency}"}`

    // We load it via a fetch in the API
    fetch(`/save_consolidation_currency`, {
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
