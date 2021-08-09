
function save(self){
    //select all tables:
    tbody_list=document.querySelectorAll(".tbody")
    nb_tables=tbody_list.length
    self.style.display="none"
    spinner_load_page.style.display="block"
    var import_array = []

    for (var t = 0; t < nb_tables; t++) {
        //make sure we are not missing any field
        tbody=tbody_list[t]
        tr_list=tbody.querySelectorAll("tr")
        length_table=tr_list.length
        contract_type_id=tbody.id
        
        for (var i = 0; i < length_table; i++) {
            contract_type_id=contract_type_id
            accounting_id=tr_list[i].children[0].children[0].value
            transaction_direction=tr_list[i].children[1].children[0].value
            pl_bs=tr_list[i].children[2].children[0].value
            dim1=tr_list[i].children[3].children[0].value
            dim2=tr_list[i].children[4].children[0].value
            market_acc=tr_list[i].children[5].children[0].value
            d_c_if_amount_positiv=tr_list[i].children[6].children[0].value
            import_array.push(`{"contract_type_id":"${contract_type_id}","transaction_direction":"${transaction_direction}","accounting_id":"${accounting_id}","dim1":"${dim1}","dim2":"${dim2}","market_acc":"${market_acc}","pl_bs":"${pl_bs}","d_c_if_amount_positiv":"${d_c_if_amount_positiv}"}`)
        } 
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
                    
                    spinner_load_page.style.display="none"
                    saved_message=document.getElementById(id="saved_message")
                    saved_message.style.display="block"
                    setTimeout(function() { 
                        saved_message.style.display="none"
                        self.style.display="block"
                        },
                    1000)
                }
            })
    
}

