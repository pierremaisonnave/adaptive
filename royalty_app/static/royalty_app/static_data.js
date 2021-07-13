

document.addEventListener('DOMContentLoaded', function() {

    document.addEventListener('click', event => {
     
        var element=event.target
        var select_all_status=document.getElementById("select_all") 
        var table = document.getElementById("static_data_table") 
        var checked_box_list=table.querySelectorAll('input[type=checkbox]')  

        //Click on select all ubtton:
        if (element.id=="select_all"){ 
            var select_mode=select_all_status.textContent 
            if (select_mode=="select_all"){
                select_all_status.textContent="unselect_all"
                checked_status=true
            }else{
                select_all_status.textContent="select_all"
                checked_status=false
            }       
            //go throug list and selec or unselect all check box
            for (i = 0; i < checked_box_list.length; ++i) {
                checked_box_list[i].checked=checked_status
                }
            file_for_export() //create a HREF in the export button
        }
        // clico on a specific checkbox
        if (element.matches('[type="checkbox"]')){
    
            if (element.checked==false){
            select_all_status.textContent="select_all"
            }else{

                checked_checkbox_list = table.querySelectorAll('input:checked')
                if (checked_checkbox_list.length == checked_box_list.length){
                  select_all_status.textContent="unselect_all"  
                }
            }

            file_for_export() //create a HREF in the export button
        }
    })

   
})





function file_for_export(){
    error_remove()

   var span_href=document.getElementById("button_extract_static")
    var span_href=document.getElementById("button_extract_static")//get the extract button( we will insert the href )
    var sheet_list_to_upload=document.getElementById("sheet_list_to_upload")//get the form( we will insert the href )
    
    var table = document.getElementById("static_data_table")   //definition os the table
    var checked_checkbox_list = table.querySelectorAll('input:checked') //in the table, get all input that are checked
    var l=checked_checkbox_list.length
    var export_file=[]

    for (i = 0; i < l; ++i) {
        var item_name=checked_checkbox_list[i].getAttribute("name")
        export_file.push(item_name)
    }



    if (l==0){span_href.removeAttribute("href")}
    else {
        span_href.href= "export/"+export_file 
        sheet_list_to_upload.value=export_file 
        }
}


function error_remove(){
   var error_message_load=document.getElementById("error_message_load")
    if (error_message_load.textContent){error_message_load.textContent=null}
}


