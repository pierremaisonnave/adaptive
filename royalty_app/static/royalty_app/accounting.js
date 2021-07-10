
function save(contract_id){
    //make sure we are not missing any field

    tbody_main_table=document.getElementById(id="tbody_main_table")
    tr_list=tbody_main_table.querySelectorAll("tr")
    length_table=tr_list.length

    var sum=0
    var import_array = []
    for (var i = 0; i < length_table; i++) {
        accounting_id=tr_list[i].children[0].children[0].value
        transaction_direction=tr_list[i].children[1].children[0].value
        pl_bs=tr_list[i].children[2].children[0].value
        dim1=tr_list[i].children[3].children[0].value
        dim2=tr_list[i].children[4].children[0].value
        dim4=tr_list[i].children[5].children[0].value
        d_c_if_amount_positiv=tr_list[i].children[6].children[0].value
        import_array.push(`{"transaction_direction":"${transaction_direction}","accounting_id":"${accounting_id}","dim1":"${dim1}","dim2":"${dim2}","dim4":"${dim4}","pl_bs":"${pl_bs}","d_c_if_amount_positiv":"${d_c_if_amount_positiv}"}`)
    } 

    import_string="["+import_array+"]"

    // We load it via a fetch in the API
    fetch(`/save_accounting`, {
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

