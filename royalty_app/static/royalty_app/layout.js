
document.addEventListener('DOMContentLoaded', function() {
    document.querySelector("main").style.visibility = "visible";  
//everytime the app open a new page, the below script identify the path ( i.e. : partners), and find the buton on the sidebar related to that page (i.e: Partners)- and then change the class name to active ( which trigger the CSS and make the button blue)
    var dictionary_={'':'1','partners':'2','contracts':'3','analytics':'4','invoices':'5','static_data':'6','settings':'7','monthly_accruals':'8','cash_flow_forecast':'9','partner_report':'10'}
    var page_path=window.location.pathname.split("/")[1] //the windows location is like: /contracts/22 , so to grab partner, we need to split by /, and take the second element
    document.getElementById(`item_in_sidebar_${dictionary_[page_path]}`).className += " active"
})

function change_profile_picture(){

    //definition od the elements
    
    spinner_top=document.getElementById('central_spinner')
    spinner_top.style.display = "Block"

    file_=document.getElementById("fileSelect_pic")
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
                spinner_top.style.display = "None"  
            }else{
                //change the profile pict of the current page
                img_list=document.getElementById('picture') 
               
                img_list.src=result.new_picture_url

                spinner_top.style.display = "None"  
            }
             
        })
    
}

function hide_dropdown_user(){
    dropdown_user=document.getElementById("dropdown_user")
    alert(dropdown_user.style.display)
    if (dropdown_user.style.display == "None"  ){
        dropdown_user.style.display = "Block"
    }

}


function spinner(){
    document.querySelector("main").style.display = "None"
    document.getElementById("spinner_load_page").style.display = "block"
    return true
}

function hide_table(table){
    document.getElementById(table).hidden=true
    document.getElementById(`hide_${table}`).hidden=true
    document.getElementById(`unhide_${table}`).hidden=false
}
function unhide_table(table){
    document.getElementById(table).hidden=false
    document.getElementById(`hide_${table}`).hidden=false
    document.getElementById(`unhide_${table}`).hidden=true
}

const cookieContainer=document.querySelector(".cookie-container")
const cookieButton=document.querySelector(".cookie-btn")
cookieButton.addEventListener("click",()=>{
    cookieContainer.classList.remove("active");
    localStorage.setItem("cookieContainerDisplayed",true)
});

setTimeout(() => {
    if (!localStorage.getItem("cookieContainerDisplayed")){
        cookieContainer.classList.add("active");
    }
}, 2000);