


const time_out_warning=document.getElementById("time_out_warning")
const main= document.querySelector("main")
const spinner_load_page=document.getElementById("spinner_load_page")
const dropdown_user= document.getElementById("dropdown_user")
const cookieContainer=document.querySelector(".cookie-container")
const cookieButton=document.querySelector(".cookie-btn")
const welcomeContainer=document.getElementById("welcomeContainer")
const background_load_page=document.getElementById("background_load_page")
const spinner_completion=document.getElementById("spinner_completion")

const is_logged_out=document.getElementById("is_logged_out").value
var is_a_login_page
//time out session : 
    const time_count_down=document.getElementById("time_count_down")
    const isuserlogged=document.getElementById("isuserlogged")
    const isconnectionpage=document.getElementById("isconnectionpage")
    const max_limit = 10*60*1000
    // visualisation of time remaining ( to be eventually remove)
        setInterval(function() {
            if (localStorage.getItem('is_user_authenticated')=='true'){
                remaining_time=(max_limit-(Date.now()-localStorage.getItem('last_reload')))/1000
                time_count_down.innerHTML=Math.floor(remaining_time/60) + ' min ;' + Math.floor(remaining_time % 60)  + ' sec'  
                isuserlogged.innerHTML=localStorage.getItem('is_user_authenticated')
                isconnectionpage.innerHTML=is_a_login_page
            }
        }, 1000); 


    //every seccond , we check if the user is loogon
    setInterval(function() {
        if (localStorage.getItem('is_user_authenticated')=='true'){  //if the user is not logged out
        var remaining_time = Date.now() -localStorage.getItem('last_reload');
        //if there is 30 sec left, then we should display a message- asking the user if he/she wants to stay logged in
            if ( remaining_time > max_limit-30*1000   ){
                time_out_warning.style.display="block"
                background_load_page.style.display="block"
            }else{ // if the user had click on stay_connected ( on another age) then the countdown start from scratch, and we must hide the warning message
                if (time_out_warning.style.display == "block"){
                    time_out_warning.style.display= null
                    background_load_page.style.display= null
                }
            }
            //if the user last action took place more than the time limit , then we should log the user out
            if ( (remaining_time > max_limit + 10000)   ){
                spinner_on()
                window.open('/automatic_logout',"_self");
            }
        }else if (is_a_login_page == false ){
            spinner_on()
            window.open('/automatic_logout',"_self");
        }
    }, 1000); // check if connected after 10 minutes and 5 seconds
    
    // if the user click on the     
    function stay_connected(){

        fetch('/isauthenticated', {method: 'GET'})
            .then(response => response.json())
            .then(result => {
                is_authenticated= result.isauthenticated
                if (is_authenticated == "YES"){
                    time_out_warning.style.display=null
                    background_load_page.style.display=null
                    localStorage.setItem('last_reload', Date.now());
                }else{
                    spinner_on()
                    window.open('/automatic_logout',"_self");
                }
            })
    }

//everytime the user click on something, it update the date
document.addEventListener('click', function() {
    if (time_out_warning.style.display == ""){ // if the warning message is on, clicking will not change anything
        fetch('/isauthenticated', {method: 'GET'})
            .then(response => response.json())
            .then(result => {
                is_authenticated= result.isauthenticated
                if (is_authenticated == "YES"){
                    localStorage.setItem('last_reload', Date.now());
                }else if (is_authenticated == "NO" & is_logged_out=='false'){
                    spinner_on()
                    window.open('/automatic_logout',"_self");
                }
            })
    }
})
document.addEventListener('DOMContentLoaded', function() {
    //ask the server if the user is looged on:
    fetch('/isauthenticated', {method: 'GET'})
        .then(response => response.json())
        .then(result => {
            is_authenticated= result.isauthenticated
            if (is_authenticated == "YES"){
                localStorage.setItem('is_user_authenticated', true);
                is_a_login_page= false
                time_count_down.innerHTML=is_a_login_page
                localStorage.setItem('last_reload', Date.now())
                //everytime the app open a new page, the below script identify the path ( i.e. : partners), and find the buton on the sidebar related to that page (i.e: Partners)- and then change the class name to active ( which trigger the CSS and make the button blue)
                var dictionary_={'':'1','partners':'2','contracts':'3','analytics':'4','invoices':'5','static_data':'6','settings':'7','monthly_accruals':'8','cash_flow_forecast':'9','partner_report':'10'}
                var page_path=window.location.pathname.split("/")[1] //the windows location is like: /contracts/22 , so to grab partner, we need to split by /, and take the second element
                document.getElementById(`item_in_sidebar_${dictionary_[page_path]}`).className += " active"
            }else{
                localStorage.setItem('is_user_authenticated', false);
                is_a_login_page= true
            }
        })


    document.querySelector("main").style.visibility = "visible";  

})


function spinner(){
    main.style.display = "None"
    background_load_page.style.display = "block"
    spinner_load_page.style.display = "block"
    return true
}
function spinner_on(){
    background_load_page.style.display = "block"
    spinner_load_page.style.display = "block"
}
function spinner_off(){
    spinner_completion.innerHTML=""
    background_load_page.style.display = "none"
    spinner_load_page.style.display = "none"
}

function change_profile_picture(){

    //definition od the elements
    spinner_load_page.style.display = "Block"
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
                spinner_load_page.style.display = "None"  
            }else{
                //change the profile pict of the current page
                img_list=document.getElementById('picture') 
                img_list.src=result.new_picture_url
                spinner_load_page.style.display = "None"  
            }     
        })
}


function spinner(){
    main.style.display = "None"
    background_load_page.style.display = "block"
    spinner_load_page.style.display = "block"
    return true
}
function spinner_on(){
    background_load_page.style.display = "block"
    spinner_load_page.style.display = "block"
}
function spinner_off(){
    background_load_page.style.display = "none"
    spinner_load_page.style.display = "none"
}


function hide_table(table){
    var content=document.getElementById(table)
    //content.style.display="block"
    $(content).slideUp(
        function(){
            //document.getElementById(table).hidden=true
            document.getElementById(`hide_${table}`).style.display="none"
            document.getElementById(`unhide_${table}`).style.display="block"
        }
    )



}
function unhide_table(table){
    var content=document.getElementById(table)
    $(content).slideDown({
        start: function () {
          $(this).css({
            display: "block"
          })
        }
      })
    document.getElementById(`hide_${table}`).style.display="block"
    document.getElementById(`unhide_${table}`).style.display="none"        

    
}
function hide_class(class_name){

    class_list=document.querySelectorAll(`.${class_name}`)
    class_list_length=class_list.length
    for (i = 0; i < class_list_length; ++i) {
        //class_list[i].hidden=true
        $(class_list[i]).slideUp()
    }
    document.getElementById(`hide_${class_name}`).style.display="none"
    document.getElementById(`unhide_${class_name}`).style.display="block"
}
function unhide_class(class_name){
    class_list=document.querySelectorAll(`.${class_name}`)
    class_list_length=class_list.length
    for (i = 0; i < class_list_length; ++i) {
        //class_list[i].hidden=false
        $(class_list[i]).slideDown()
    }
    document.getElementById(`hide_${class_name}`).style.display="block"
    document.getElementById(`unhide_${class_name}`).style.display="none"
}

//Cookie

cookieButton.addEventListener("click",()=>{
    cookieContainer.classList.remove("active");
    localStorage.setItem("cookieContainerDisplayed",true)
});

setTimeout(() => {
    if (!localStorage.getItem("cookieContainerDisplayed")){
        cookieContainer.classList.add("active");
    }
}, 1000);

//Welcome message when on "Login page"

setTimeout(() => {
    if (welcomeContainer){
        welcomeContainer.classList.add("active")
    }
}, 2000);
setTimeout(() => {
    if (welcomeContainer){
        welcomeContainer.classList.remove("active")
    }
}, 10000);


function openlink(self){
    dropdown_user.style.display = "None"
    spinner()
    redirect=self.getAttribute("redirect")
    url=self.getAttribute("url")
    fetch('/isauthenticated', {method: 'GET'})
        .then(response => response.json())
        .then(result => {
            
            if (result.isauthenticated=="YES"){
                window.open(url,"_self");
            }else{
                window.open(redirect,"_self");
            }
        })

}

function isauthenticated_form(form){
    redirect=form.getAttribute("redirect")
    //goal is to check if user is already authentified, if so we redirect user to home page
    fetch('/isauthenticated', {method: 'GET'})
    //retreive the partner ID  (result.partner_id ) and create the additional row
        .then(response => response.json())
        .then(result => {
            spinner()
            if (result.isauthenticated=="NO"){
                form.submit();
            }else{
                window.open(redirect,"_self");
            }
            
        })    
}


// for a smooth transition when user remove live
function smooth_remove_row(tr_to_delete,table){
    $(tr_to_delete)
        .children('td, th')
        .animate({
        padding: 0
    })
        .wrapInner('<div />')
        .children()
        .slideUp(function () {
            table.row( tr_to_delete ).remove().draw(false);  
    });
}
function smooth_remove_row_nodatatable(tr_to_delete){
    $(tr_to_delete)
        .children('td, th')
        .animate({
        padding: 0
    })
        .wrapInner('<div />')
        .children()
        .slideUp(function () {
            tr_to_delete.remove();  
    });
}

// ----------------Code to change tab within a page--------------
const chevron_list=document.querySelectorAll('.chevron')
const chevron_length= chevron_list.length

const graph_input_list=document.querySelectorAll('.graph_input')
const graph_input_length= graph_input_list.length
const form_new_partner=document.getElementById('form_new_partner')

const content_list=document.querySelectorAll('.content')
const content_length= content_list.length
const icon_list=document.querySelectorAll('.icon')
const icon_length= icon_list.length

function change_tab(tab,){

    if (tab=="all"){
        // unhide all chevron
        for (ch = 0; ch < chevron_length; ++ch) {
            chevron_list[ch].hidden=false
            chevron_list[ch].children[0].style.display="none"
            chevron_list[ch].children[1].style.display="block"
        }
        //unhide all content
        for (c = 0; c < content_length; ++c) {
            content_list[c].style.display="block"
        }
        // for Dashboard, change the graph-imput class to pink
        for (g = 0; g < graph_input_length; ++g) {  
            graph_input_list[g].classList.remove("graph_input_pink")
            graph_input_list[g].classList.add("graph_input")
        }
        // if in contract or partner tab, we should hide/unhide the form when we go on a specific tab
        if (form_new_partner !=null){
            form_new_partner.hidden=true
        }
    }else{
        // hide all chevron
        for (ch = 0; ch < chevron_length; ++ch) {
            chevron_list[ch].hidden=true
        }
        //hide all content
        for (c = 0; c < content_length; ++c) {
            content_list[c].style.display="none"
        }
        //unhide all tabs:

        var tab_list = document.querySelectorAll(`.${tab}`)
        var tab_list_lenght = tab_list.length
        for (ta = 0; ta < tab_list_lenght; ++ta) {
            tab_list[ta].style.display="block"
        }
        // for Dashboard, change the graph-imput class to pink
        for (g = 0; g < graph_input_length; ++g) {  
            graph_input_list[g].classList.remove("graph_input")
            graph_input_list[g].classList.add("graph_input_pink")
        }
        // if in contract or partner tab, we should hide/unhide the form when we go on a specific tab
        if (form_new_partner !=null){
            form_new_partner.hidden=false
        }
    }

    //change color of all intem-contract
        var selected_icon_list = document.querySelectorAll(`.icon_${tab}`)
        var selected_icon_list_lenght = selected_icon_list.length
    
        for (b = 0; b < icon_length; ++b) {
            c=icon_list[b].children[0]
            i=c.children[0]
            c.style.backgroundColor  = null;
            c.style.color  = null;
            i.style.color  = null;
            c.style.border  = null;
        }
        for (si = 0; si < selected_icon_list_lenght; ++si) {
            circle=selected_icon_list[si].children[0]
            icon=circle.children[0]
            circle.style.backgroundColor  = "red";
            circle.style.color  = "red";
            icon.style.color  = "white";
            circle.style.border  = "solid 2px red";
        }
}
const contract_icon_list=document.querySelectorAll('.contract_icon')
const contract_icon_length= contract_icon_list.length
const contract_tab_list=document.querySelectorAll('.contract_tab')
const contract_tab_length= contract_tab_list.length
function change_contract_tab(button,tab){
    //hide all content
        for (c = 0; c < contract_tab_length; ++c) {
            contract_tab_list[c].style.display="none"
        }
        document.getElementById(tab).style.display="block"
    //change color of all intem-contract

        for (b = 0; b < contract_icon_length; ++b) {
            c=contract_icon_list[b].children[0]
            i=c.children[0]
            c.style.backgroundColor  = null;
            c.style.color  = null;
            i.style.color  = null;
            c.style.border  = null;
        }
        circle=button.children[0]
        icon=circle.children[0]
        circle.style.backgroundColor  = "red";
        circle.style.color  = "red";
        icon.style.color  = "white";
        circle.style.border  = "solid 2px red";
}




const dashboard_list=document.querySelectorAll(".form_dashboard")
const dashboard_list_length=dashboard_list.length
const chevron_hide_list=document.querySelectorAll(".chevron_hide")
const chevron_hide_list_length=chevron_hide_list.length
const chevron_unhide_list=document.querySelectorAll(".chevron_unhide")
const chevron_unhide_list_length=chevron_unhide_list.length
const top_chevron_row_list=document.querySelectorAll(".top_chevron_row")
const top_chevron_list=document.querySelectorAll(".top_chevron")
const top_chevron_row_list_length=top_chevron_row_list.length

function unhide_dashboard(){
    //slide up,down all dashboard:
    for (cont = 0; cont < dashboard_list_length; ++cont){
        $(dashboard_list[cont]).slideDown()
    }
    //hide /unhide chevron
    for (ch = 0; ch < chevron_hide_list_length; ++ch){
        chevron_hide_list[ch].style.display="block"
    }
    for (cu = 0; cu < chevron_unhide_list_length; ++cu){
        chevron_unhide_list[cu].style.display="none"
    }
    // change color of dashboard and add/remove border
    for (c = 0; c < top_chevron_row_list_length; ++c){
        var top_chevron=top_chevron_list[c]
        top_chevron_row_list[c].style.backgroundColor=null
        top_chevron.style.border=null
        top_chevron_row_list[c].style.height=null
    }
}
function hide_dashboard(){
    //slide up,down all dashboard:
    for (cont = 0; cont < dashboard_list_length; ++cont){
        $(dashboard_list[cont]).slideUp()
    }
    //hide /unhide chevron
    for (ch = 0; ch < chevron_hide_list_length; ++ch){
        chevron_hide_list[ch].style.display="none"
    }
    for (cu = 0; cu < chevron_unhide_list_length; ++cu){
        chevron_unhide_list[cu].style.display="block"
    }
    // change color of dashboard and add/remove border
    for (c = 0; c < top_chevron_row_list_length; ++c){
        var top_chevron=top_chevron_list[c]
        top_chevron_row_list[c].style.backgroundColor="rgb(255, 239, 239)"
        top_chevron.style.border="transparent"
        //top_chevron_row_list[c].style.height="14px"
    }
}

