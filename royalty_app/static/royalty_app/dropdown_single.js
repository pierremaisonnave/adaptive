
document.addEventListener('DOMContentLoaded', function() {

    document.addEventListener('click', event => {
        var element = event.target;
        
        //hide all dp 
        if (!isindropdownlist(event)){  //we verify if the user click inside a dd- if so, we do not hide all dd

            hidde_all_dropdows()
        }
         
        var classnameparent=element.parentElement.className;
        var classname=element.className;
        var dd_id = element.getAttribute("dd_id")
        const region_id = element.getAttribute("region_id")
        
        if (isindropdownlist(event) ){ 
            //hide or unhide a region
            if (classname.includes("comboTreeParentPlus")){
                unhideregion(dd_id,region_id,element)}
            //if user click on item, then we must change the input box
            if (classname=="item_single_select" || classnameparent=="item_single_select"){
                if (classnameparent=="item_single_select"){e=element.parentElement}else{e=element}
                var dd_id = e.getAttribute("dd_id")

                text_box=document.getElementById(`displayed_item_name_${dd_id}`)
                hidden_item_code=document.getElementById(`hidden_item_code_${dd_id}`)

                text_box.value= e.childNodes[3].textContent // in the textbook input ( visible) we display the item name
                hidden_item_code.value=e.childNodes[1].textContent // in the textbook input ( invisible) we display the item code
                hidde_all_dropdows()
                
            }
            if (element.parentElement==null ){return} // if we click on an object without parent, we stop
        }

        if (classnameparent == "comboTreeInputWrapper"   ) {
            // is dropdown hidden?
            var dd_item=document.getElementById(`dropdown_${dd_id}`)
            if (dd_item.style.display === "block"){dd_item.style.display = "none"} else { dd_item.style.display = "block"} 
        }  

        if ( element.id=="user_menu" || element.id=="user_photo_on_layout") {
            // is dropdown hidden?
            dropdown_user=document.getElementById(`dropdown_user`)
            if (dropdown_user.style.display === "block"){dropdown_user.style.display = "none"} else { dropdown_user.style.display = "block"} 
        }     
    })

    //search box when typing
     document.addEventListener('input', event => {
         var element = event.target;
         var searched_value=element.value.toUpperCase()
         var dd_id = element.getAttribute("dd_id")
        
         if (element.className  == "multiplesFilter"){
            hideitemsearch(dd_id,searched_value)
            
         }
     })

})

function hideitemsearch(dd_id,searched_value){
    var dd_item=document.getElementById(`dropdown_${dd_id}`)
    item_list=dd_item.querySelectorAll('.item_single_select')
    //alert(check_box_list.length)
        for (i = 0; i < item_list.length; ++i) {

        string_item=item_list[i].textContent.toUpperCase()
        
        if(string_item.includes(searched_value)) {

            item_list[i].style.display="block"
        }else {
            item_list[i].style.display="none"
        }

    }
}

function unhideregion(dd_id,region_id,element){
    

    var e=document.getElementById(dd_id + '_' + region_id)
    if (e.style.display=== "block"){
        e.style.display = "none"
        element.setAttribute('class', 'bi-arrow-right-circle comboTreeParentPlus');
        }
    else {
        e.style.display = "block"
        element.setAttribute('class', 'bi-arrow-down-circle comboTreeParentPlus');
        } 
}

 
function isindropdownlist(event){
    var e= event.target;
    if (e.className.includes("comboTreeInputBox")){
        grandparentelement=e.parentElement.parentElement
        if (grandparentelement.childNodes[3].style.display=="block"){return true}
    }
    if (e.id== "user_menu" || e.id=="user_photo_on_layout"){
        dropdown_user=document.getElementById(`dropdown_user`)
        if (dropdown_user.style.display=="block"){return true }
    }

    node=e.parentNode
    while (node != null){
        if (node.className=="comboTreeDropDownContainer") {return true }else{}
        node = node.parentNode;
    }

    return false   
}

function hidde_all_dropdows(){
    dd_list= document.querySelectorAll(".comboTreeDropDownContainer")
    for (h = 0; h < dd_list.length; ++h) {
        dd_list[h].style.display = "none"
    }
    search_list=document.querySelectorAll(".multiplesFilter")
    for (h = 0; h < search_list.length; ++h) {

        var dd_id=search_list[h].getAttribute("dd_id")
        search_list[h].value=""
        hideitemsearch(dd_id,"")
    }
}

