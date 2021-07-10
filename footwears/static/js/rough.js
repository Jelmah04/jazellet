
document.addEventListener('DOMContentLoaded',function () {
    document.querySelector('.wishthis').onclick = function () {
      alert('This is just a step')
    }
  } )
  
  
  
  
  
  if(!localStorage.getItem('counter'))
  localStorage.setItem('counter', 0);
  print('gotten the local storage')
  
    document.addEventListener('DOMContentLoaded', ()=>{
      document.querySelector('#counter').innerHTML=localStorage.getItem('counter');
  
      document.querySelectorAll('.wishthis').onclick = ()=>{
        let counter = localStorage.getItem('counter');
        counter ++;
        print("here is counter++")
        document.querySelector('#counter').innerHTML = counter;
        localStorage.setItem('counter', counter);
        print('counter is' + counter)
      }
  });
  
  
  
  
  // alert('hello my dearies')
    
    //   alert('{{ paystack_key }}');
    // paymentForm = document.getElementById('btn-pay');
    // print('got btn-pay as ' + paymentForm)
    // paymentForm.addEventListener("click", payWithPaystack, false);
  
  //   function payWithPaystack() {
  //         // e.preventDefault();
  //         // var user_amount = $("#price").val();
  //         let handler = PaystackPop.setup({
  //             key: 'pk_test_f9d521d0cf9be5abb26d59e9d6340b759183a40e', // Replace with your public key
  //             email: '{{ user.email }}',
  //             amount: document.getElementById('price').value  * 100,
  //             currency: 'NGN',
  //             ref: ''+Math.floor((Math.random() * 1000000000) + 1), // generates a pseudo-unique reference. Please replace with a reference you generated. Or remove the line entirely so our API will generate one for you,            
  //             // label: "Optional string that replaces customer email"
  //             onClose: function(){
  //                 alert('Payment Cancelled.');
  //             },
  //             callback: function(response){
  //               console.log(response);
  //                 $.ajax({
  //                     url: 'http://localhost/verify_transaction?reference='+ response.reference,
  //                     method: 'get',
  //                     success: function (res) {
  //                       console.log(res);
  //                         // the transaction status is in response.data.status
  //                         if(res.data.status == 'success') {
  //                             let message = 'Payment completed!    Thanks.\n \n \nClick OK to Continue';
  //                             alert(message);
  //                             // location.reload();
  //                         } else {
  //                             let message = 'Payment was not completed! Click OK to Try Again';
  //                             alert(message);
  //                             // location.reload();
  //                         }
  //                     }
  //                 });
                  
  //             }
  //         });
  //         handler.openIframe();
  //     }
  
  // // <!--Ending of other parts for funding  -->
  
  
  
  
  
  
  
  
  
  
  
  
  
  