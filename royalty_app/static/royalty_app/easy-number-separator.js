document.addEventListener('DOMContentLoaded', function() {
  $(document).on('input', '.number-separator', function (e) {
      if (this.value.substring(0, 1)=="-"){
        n="-";
      this.value=this.value.substring(1)
      }else{n=""}
      string_amount=this.value.toString()
      string_amount=string_amount.replaceAll(",","")
      string_amount=string_amount.replaceAll("-","")
      string_amount=string_amount.replace(/[^\d.-]/g, '')
      string_amount=string_amount.replace(/\B(?<!\.\d*)(?=(\d{3})+(?!\d))/g, ",");
      this.value=n+string_amount
 });
});