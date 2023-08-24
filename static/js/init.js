

   


(function($){
    $(function(){
        
        var lat = null;
        var long = null;
        navigator.geolocation.getCurrentPosition((position) => {
            lat = position.coords.latitude;
            long = position.coords.longitude;
            
            $('#lat').val(lat);
            $('#long').val(long);
            console.log(lat);
            console.log(long);
          },(error)=> {
            if (error.PERMISSION_DENIED) {
                console.log("Error: permission denied");
                // Your custom modal here.
                
                while(lat==null){
                    alert('Geolocation is not enabled. Please enable to use this application and reopen in another tab.');
                }
                
              } else {
                // Handle other kinds of errors.
                console.log("Other kind of error: " + error);
              }
          });


      
        setTimeout(function() {
            $('#main').attr("hidden",false);
            $('#loader').attr("hidden",true); // Do something after 5 seconds
       }, 200);



       $('#nextButton').click(function(){
        $('#nextButton').attr("hidden",true);
        $('#info').attr("hidden",true);
        $('#ques').attr("hidden",false);
        $('#backButton').attr("hidden",false);
        $('#submit').attr("hidden",false);
       });

       $('#backButton').click(function(){
        $('#nextButton').attr("hidden",false);
        $('#info').attr("hidden",false);
        $('#ques').attr("hidden",true);
        $('#backButton').attr("hidden",true);
        $('#submit').attr("hidden",true);
       });

       $("#otp").on('keyup',function (){

        if($('#otp').val() == otp){
            $('.message2').attr('uk-icon', 'check');
            $('.message2').css('color', 'green');
        }
        else{
            $('.message2').attr('uk-icon', 'close');
            $('.message2').css('color', 'red');
        }

       });

       $('#pass, #pass2, #otp').on('keyup', function () {
        if ($('#pass').val() == $('#pass2').val() && $('#otp').val() == otp && $('#pass').val() != "") {
            $('.message').attr('uk-icon', 'check');
          $('.message').css('color', 'green');
          $('#chngpass').prop('disabled',false);
          
        } else {
            $('.message').attr('uk-icon', 'close');
          $('.message').css('color', 'red');
          $('#chngpass').prop('disabled',true);
          
        }
      });
       
       UIkit.upload('.js-upload', {

        url: '/upload',
        mime: "image/*",
        


        beforeSend: function (environment) {
            console.log('beforeSend', arguments);

            // The environment object can still be modified here.
            // var {data, method, headers, xhr, responseType} = environment;

        },
        beforeAll: function () {
            console.log('beforeAll', arguments);
        },
        load: function () {
            console.log('load', arguments);
        },
        error: function () {
            console.log('error', arguments);
        },
        complete: function () {
            console.log('complete', arguments);
        },

        loadStart: function (e) {
            console.log('loadStart', arguments);

            bar.removeAttribute('hidden');
            bar.max = e.total;
            bar.value = e.loaded;
        },

        progress: function (e) {
            console.log('progress', arguments);

            bar.max = e.total;
            bar.value = e.loaded;
        },

        loadEnd: function (e) {
            console.log('loadEnd', arguments);

            bar.max = e.total;
            bar.value = e.loaded;
        },

        completeAll: function () {
            console.log('completeAll', arguments);
              var uid = $('#uid').val();
              console.log('static/uploads/'+uid+'.png');
            $('.pic').attr('src','static/uploads/'+uid+'.png');
            

            alert('Upload Completed');
        }

    });

  
      
  
    }); // end of document ready
  
  })(jQuery); // end of jQuery name space
  
  

  
  
  