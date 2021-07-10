function add_new_row(elm){
    //check that the value do not already exist
        if (is_unique(elm) ==false){
            alert("this primary key already exist, please choose another one");
            elm.value="" ;
            return}
    //set a new"previous value" this value will be used to reset the imput in case of wrong typing        
        elm.setAttribute('previous_value',elm.value) 
    // verify that from and two are not empty
        elm_tr=elm.parentElement.parentElement
        elm_from=elm_tr.children[0].children[0]
        elm_to=elm_tr.children[1].children[0]
        elm_rate=elm_tr.children[2].children[0]
        if ((elm_from.value=="")||(elm_to.value=="")||(elm_rate.value=="")){return}
    //select the row and table
        new_tr=document.getElementById(id="new_tr")
        main_table=document.getElementById(id="main_table")
    //remove id and onchange action + unhide button
        new_tr.removeAttribute('id');
        elm_from.removeAttribute('onchange')
        elm_from.setAttribute('onchange', "is_unique_key(this)") 
        elm_to.removeAttribute('onchange')
        elm_to.setAttribute('onchange', "is_unique_key(this)") 
        elm_rate.removeAttribute('onchange')
        new_tr.children[3].children[0].hidden=false
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

    // column 3 select, clone and insert Select
        var itm = document.getElementById("column_3").children[0];
        var cln = itm.cloneNode(true);
        newCell = newRow.insertCell(3);
        newCell.appendChild(cln)
}

function delete_row(elm){
    elm.parentNode.parentNode.remove()
}

function save(contract_id){
    //make sure we are not missing any field

    //check if total =100
    tbody_main_table=document.getElementById(id="tbody_main_table")
    tr_list=tbody_main_table.querySelectorAll("tr")
    length_table=tr_list.length-1

    var sum=0
    var import_array = []
    for (var i = 0; i < length_table; i++) {
        country_from=tr_list[i].children[0].children[0].value
        country_to=tr_list[i].children[1].children[0].value
        wht_rate=tr_list[i].children[2].children[0].value
        import_array.push(`{"country_from":"${country_from}","country_to":"${country_to}","wht_rate":"${wht_rate}"}`)
    } 

    import_string="["+import_array+"]"

    // We load it via a fetch in the API
    fetch(`/save_tax`, {
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


function thousands_separators(num)
  {
    var num_parts = num.toString().split(".");
    num_parts[0] = num_parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    return num_parts.join(".");
  }

function convert_percentage(elm){
  var num = Number(elm.value);
  elm.value=num.toFixed(2)
}

function is_unique(elm){
    //definition of the from/to of the selected row
    elm_tr=elm.parentElement.parentElement
    elm_from=elm_tr.children[0].children[0].value
    elm_to=elm_tr.children[1].children[0].value

    //loop thought the rows, and make sure that the combination from/to only appear one
    tbody_main_table=document.getElementById(id="tbody_main_table")
    tr_list=tbody_main_table.querySelectorAll("tr")
    length_table=tr_list.length

    n=0
    for (var i = 0; i < length_table; i++) {
        from_item=tr_list[i].children[0].children[0].value
        to_item=tr_list[i].children[1].children[0].value
        if ((elm_from== from_item) &&(elm_to==to_item))
            n++
        } 

    if (n!=1){return false} else{return true}   
}
function is_unique_key(elm){

    if (is_unique(elm) ==false){
        alert("this primary key already exist, please choose another one"); 

        elm.value=elm.getAttribute("previous_value")
        return}else{
        elm.setAttribute("previous_value",elm.value )  
        }
}

