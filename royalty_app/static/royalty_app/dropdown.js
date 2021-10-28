
document.addEventListener('DOMContentLoaded', function() {
    document.addEventListener('click', event => {
        var element = event.target;
        var comboTreeWrapper = null
        var comboTreeInputWrapper = null
        var comboTreeDropDownContainer = null

        //find the comboTreeWrapper 
        comboTreeWrapper=get_comboTreeWrapper_list(element)
        
        var isindd= false
        if (comboTreeWrapper){
            comboTreeInputWrapper=comboTreeWrapper.querySelector(".comboTreeInputWrapper")
            comboTreeDropDownContainer=comboTreeWrapper.querySelector(".comboTreeDropDownContainer")
            comboTreeInputBox=comboTreeWrapper.querySelector(".comboTreeInputBox")
            comboTreeHiddenBox=comboTreeWrapper.querySelector(".comboTreeHiddenBox")
            var multiplesFilter=comboTreeWrapper.querySelector(".multiplesFilter")
            //find if user clicked in the dd menu
            isindd= comboTreeDropDownContainer.contains(element)
        }
    
        if (isindd){ 
            // if click on a checkbox ( multi choice)
            if (element.matches('[type="checkbox"]')){
                actiononcheckbox(comboTreeWrapper)
            }
            //if user click on item ( single choice)
            li_list=comboTreeDropDownContainer.querySelectorAll('li')
            li_list_lenght=li_list.length
            for (li = 0; li < li_list_lenght; ++li) {
                if (li_list[li].contains(element) & li_list[li].className.includes("item_single_select")){
                    comboTreeInputBox.value= li_list[li].getAttribute("item_display") 
                    comboTreeHiddenBox.value= li_list[li].getAttribute("item_code") 
                }
            }
            // if user click on a group ( multi choice) we must select all checkbox
            if (element.getAttribute("class") == "group"){
                item_group = element.parentElement.querySelectorAll('input[type=checkbox]')
                checked_item = element.parentElement.querySelectorAll('input:checked')
                if(checked_item.length >0){
                    for (i = 0; i < checked_item.length; ++i) {
                        checked_item[i].checked=false
                    }
                }else{
                    for (i = 0; i < item_group.length; ++i) {
                        item_group[i].checked=true
                    }
                }
                actiononcheckbox(comboTreeWrapper)
            }
            //if user click on the group icon ( multi choice + single choice)
            if (element.className.includes("comboTreeParentPlus")){ 
                unhidegroup(element)}

        }else{  
            //close all dd
            //we verify if the user click inside a dd OR on a cell with class "hidden_dd_"- if not, we  hide all dd
            dd_list= document.querySelectorAll(".comboTreeDropDownContainer")
            for (i = 0; i < dd_list.length; ++i) {
                if ( dd_list[i] !=comboTreeDropDownContainer ){
                    dd_list[i].style.display = "none"
                }
            }

            //find the comboTreeWrapper 
            var comboTreeWrapper_list=document.querySelectorAll(".comboTreeWrapper")
            var comboTreeWrapper_length=comboTreeWrapper_list.length
            for (ct = 0; ct < comboTreeWrapper_length; ++ct) { 
                Filterinput=comboTreeWrapper_list[ct].querySelector(".multiplesFilter")
                if(Filterinput){
                    Filterinput.value=""
                    hidesearch(comboTreeWrapper_list[ct],"")
                }
            }

            //if click in input /div item
            if (comboTreeInputWrapper){
                if (comboTreeInputWrapper.contains(element) ) {
                    // is dropdown hidden?
                    if (comboTreeDropDownContainer.style.display === "block"){comboTreeDropDownContainer.style.display = "none"
                    } else { 
                        comboTreeDropDownContainer.style.display = "block"
                        if (multiplesFilter){
                            multiplesFilter.focus();
                            multiplesFilter.select();
                        }
                    } 
                } 
            }
        }

 
   
    })

    //search box when typing
     document.addEventListener('input', event => {
         var element = event.target;
         var searched_value=element.value.toUpperCase()
         comboTreeWrapper=get_comboTreeWrapper_list(element)
         if (element.className  == "multiplesFilter"){
            hidesearch(comboTreeWrapper,searched_value)     
         }
     })
})


function get_comboTreeWrapper_list(element){
        //find the comboTreeWrapper 
        var comboTreeWrapper_list=document.querySelectorAll(".comboTreeWrapper")
        var comboTreeWrapper_length=comboTreeWrapper_list.length
        for (ct = 0; ct < comboTreeWrapper_length; ++ct) { 
            if (comboTreeWrapper_list[ct].contains(element)){
                comboTreeWrapper=comboTreeWrapper_list[ct]
                return comboTreeWrapper
            }
        }
        return false
}

function hidesearch(comboTreeWrapper,searched_value){

    // loop thtough all li and hide/undie
    li_list=comboTreeWrapper.querySelectorAll('li')
    li_list_length=li_list.length
        for (li = 0; li < li_list_length; ++li) {
            if (li_list[li].className.includes("selection_mode") == false ){
                string_item=li_list[li].textContent.toUpperCase()
                if(string_item.includes(searched_value)) {
                    li_list[li].style.display="block"
                }else {
                    li_list[li].style.display="none"
                }
            }
    }
    // unhide all ul (group)
    ul_list=comboTreeWrapper.querySelectorAll('ul')
    ul_list_length=ul_list.length
        for (ul = 0; ul < ul_list_length; ++ul) {
            ul_list[ul].style.display="block"
        }

    //chanve the chevron 
    chevron_right_list=comboTreeWrapper.querySelectorAll('.bi-chevron-right') 
    chevron_right_list_lenght=chevron_right_list.length
        for (ch = 0; ch < chevron_right_list_lenght; ++ch) {
            chevron_right_list[ch].setAttribute('class', 'bi bi-chevron-down comboTreeParentPlus');
        }
}

function unhidegroup(element){
    
    var e1=element.parentElement.querySelector("ul")
    if (e1.style.display=== "block"){
        e1.style.display = "none"
        element.setAttribute('class', 'bi bi-chevron-right comboTreeParentPlus');
        }
    else {
        e1.style.display = "block"
        element.setAttribute('class', 'bi bi-chevron-down comboTreeParentPlus');
        } 
}


function actiononcheckbox(comboTreeWrapper){
    comboTreeInputWrapper=comboTreeWrapper.querySelector(".comboTreeInputWrapper")
    comboTreeDropDownContainer=comboTreeWrapper.querySelector(".comboTreeDropDownContainer")
    comboTreeInputBox=comboTreeWrapper.querySelector(".comboTreeInputBox")
    comboTreeHiddenBox=comboTreeWrapper.querySelector(".comboTreeHiddenBox")

    var select_all_box=comboTreeWrapper.querySelector(".select_all_box")
    var selection_mode_input=comboTreeWrapper.querySelector(".selection_mode_input")
    display_list=[]
    hidden_list=[]

    //Select All or None
    if (select_all_box.checked){
        selection_mode_input.value= "EXCLUDE"
    }else{
        selection_mode_input.value= "INCLUDE"
    }    
    // loop throug all checked checkbox ( to the expection of "select All" box)
    checked_item = comboTreeWrapper.parentElement.querySelectorAll('input:checked')
    checked_item_length=checked_item.length
    for (c = 0; c < checked_item_length; ++c) {
        if (checked_item[c] != select_all_box){
            display_list.push(checked_item[c].getAttribute("item_display"))
            hidden_list.push(checked_item[c].getAttribute("item_code"))
        }
    }

    // loop thoug all textbox, and prepare the input and hidden list
    if(hidden_list[0]==""){hidden_list.splice(0,1)}           
    hidden_list = hidden_list.join(', ')
    display_list = display_list.join(', ')
    comboTreeInputBox.style.color=null
    comboTreeHiddenBox.value=hidden_list
    if (selection_mode_input.value == "INCLUDE"){
        if (hidden_list == ""){
            comboTreeInputBox.innerHTML="Select"
            comboTreeInputBox.style.color="grey"
        }else{
            comboTreeInputBox.innerHTML=display_list
        }
    }else if(selection_mode_input.value == "EXCLUDE"){
        if (hidden_list == ""){
            comboTreeInputBox.innerHTML="All"
        }else{
            comboTreeInputBox.innerHTML='All except : '+ display_list
        }
    }
}