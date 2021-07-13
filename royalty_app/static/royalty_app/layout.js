
document.addEventListener('DOMContentLoaded', function() {
    document.querySelector("main").style.visibility = "visible";  
//everytime the app open a new page, the below script identify the path ( i.e. : partners), and find the buton on the sidebar related to that page (i.e: Partners)- and then change the class name to active ( which trigger the CSS and make the button blue)
    var dictionary_={'':'1','partners':'2','contracts':'3','analytics':'4','invoices':'5','static_data':'6','settings':'7','monthly_accruals':'8','cash_flow_forecast':'9','partner_report':'10'}
    var page_path=window.location.pathname.split("/")[1] //the windows location is like: /contracts/22 , so to grab partner, we need to split by /, and take the second element
    document.getElementById(`item_in_sidebar_${dictionary_[page_path]}`).className += " active"
})

function change_profile_picture(){

    //definition od the elements

    file_=document.getElementById("fileSelect")
    name_file=file_.files[0].name

    
    let formData = new FormData();
    formData.append('file', file_.files[0], name_file);

    //book in database
    fetch('/new_profile_pict', {
        method: 'POST',
        body: formData
        })
    //retreive the partner ID  (result.partner_id ) and create the additional row
        .then(response => response.json())
        .then(result => {
            if (result.error){
            }else{
                //change the profile pict of the current page
                img_list=document.querySelectorAll('.user_img') 
                for ( var img = 0; img < img_list.length; img++){
                    img_list[img].src=result.new_picture_url
                }
                }   
        })
    
}
