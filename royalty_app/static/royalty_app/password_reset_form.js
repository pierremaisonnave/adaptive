document.addEventListener('DOMContentLoaded', function() {
    document.addEventListener('change', function() {
        captcha_div=document.getElementById("captcha")
        required_list=document.querySelectorAll("[required]")
        n=0
        for (i = 0; i < required_list.length; ++i) {
            if (required_list[i].value==""){n=n+1}
        }
        print
        if (n == 0 && captcha_div.style.display=='none'){captcha_div.style.display='block'} 

    })
})

function validateRecaptcha() {
    var response = grecaptcha.getResponse();
    if (response.length === 0) {
        alert("Please validate CAPTCHA");
        return false;
    } else {
        return true;
    }
}
