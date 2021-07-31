
document.addEventListener('DOMContentLoaded', function() {
    
    
 


    document.addEventListener('click', event => {
        var element = event.target;


        //hide all dp 
        if (!isindropdownlist(event)){  //we verify if the user click inside a dd OR on a cell with class "hidden_dd_"- if not, we  hide all dd

            dd_list= document.querySelectorAll(".comboTreeDropDownContainer")

            for (i = 0; i < dd_list.length; ++i) {
              dd_list[i].style.display = "none"
            }
            search_list=document.querySelectorAll(".multiplesFilter")

            for (i = 0; i < search_list.length; ++i) {
                var dd_id=search_list[i].getAttribute("dd_id")

                search_list[i].value=""
                hidesearch(dd_id,"")
            }
            
            if (element.parentElement==null ){return} // if we click on an object without parent, we stop
        }
        
        var classnameparent=element.parentElement.className;
        var classname=element.className;
        var dd_id = element.getAttribute("dd_id")
        const group_id = element.getAttribute("group_id")
        
        if (isindropdownlist(event) ){ 
            
            // if click on a checkbox
            if (element.matches('[type="checkbox"]')){
                actiononcheckbox(dd_id,element)
            }
            if (element.getAttribute("class") == "group"){
                item_group = element.parentElement.querySelectorAll('input[type=checkbox]')
                checked_item = element.parentElement.querySelectorAll('input:checked')
                if(checked_item.length >0){
                    for (i = 0; i < checked_item.length; ++i) {
                        checked_item[i].checked=false
                        actiononcheckbox(dd_id,checked_item[i])
                    }
                }else{
                    for (i = 0; i < item_group.length; ++i) {
                        item_group[i].checked=true
                        actiononcheckbox(dd_id,item_group[i])
                    }
                }
            }
            //hide or unhide a group
            if (classname.includes("comboTreeParentPlus")){
                
                unhidegroup(dd_id,group_id,element)}
        }
        if (classnameparent == "comboTreeInputWrapper"  ) {
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
            hidesearch(dd_id,searched_value)
            
         }
     })
})

function hidesearch(dd_id,searched_value){
    var dd_item=document.getElementById(`dropdown_${dd_id}`)
    check_box_list=dd_item.querySelectorAll('input[type=checkbox]')
    
        for (n = 1; n < check_box_list.length; ++n) {
        parent_li=check_box_list[n].parentElement
        string_item=parent_li.textContent.toUpperCase()
        
        if(string_item.includes(searched_value)) {

            parent_li.style.display="block"
        }else {
            parent_li.style.display="none"
        }

    }
}

function unhidegroup(dd_id,group_id,element){
    

    var e=document.getElementById(dd_id + '_' + group_id)

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
        if (grandparentelement && grandparentelement.children[1].style.display=="block"){return true}

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

function actiononcheckbox(dd_id,element){
    var text_box_dd=document.getElementById(`item_list_display_${dd_id}`)
    var item_list_input=document.getElementById(`item_list_${dd_id}`)
    var item_value=item_list_input.value
    var select_mode_box=document.getElementById(`select_mode_${dd_id}`)
    var item_list = item_value.split(',');


    if ( select_mode_box !== element){ // in case we use a "select all" option
        var item_code=element.nextSibling.innerHTML
        var checked_status=element.checked
        
        //If we check a box
        if (checked_status){item_list.push(item_code)}
        //If we uncheck a box
        else{
            item_remove=item_list.indexOf(item_code);
            item_list.splice(item_remove, 1);     
        }
    }
    if(item_list[0]==""){item_list.splice(0,1)}           
    item_list_input.value=item_list
    if (select_mode_box.checked){
        if (item_list.length==0){text_box_dd.value="All"}else{text_box_dd.value='All except : '+ item_list }
        
        }else{
        text_box_dd.value=item_list
    }    
     
}