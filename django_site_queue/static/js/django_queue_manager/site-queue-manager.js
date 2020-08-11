var sitequeuemanager  = { 
     var: {
        'queueurl': 'false',
        'running': 'false',
        'url': '',
        'session_key': '' 
     },
     check_queue: function() {
        sitequeuemanager.var.running = 'true';

        $.ajax({
          url: sitequeuemanager.var.url+'/api/check-create-session/?session_key='+sitequeuemanager.var.session_key,
          type: 'GET',
          data: {},
          cache: false,
          success: function(response) { 
            if (response.status == "Active")  {
                  if (response['session_key'] != sitequeuemanager.var.session_key) {
                     $('#site_queue_frame').html('<iframe src="'+sitequeuemanager.var.url+"/site-queue/set-session/?session_key="+response['session_key']+'" title="Set Session"></iframe>');
                  }

                  sitequeuemanager.var.session_key = response['session_key'];
                  
                  if (sitequeuemanager.var.queueurl == 'true') {
                      window.location=response.url+"/?session_key="+response['session_key'];
                  }
	    } else {
                  if (sitequeuemanager.var.queueurl == 'true') {
                      sitequeuemanager.var.session_key = response['session_key'];
                      if (response['queue_position'] > 0 ) { 
                          $('#queue_position_div').show();
                          $('#queue_position').html(response['queue_position']);
                      }
                  } else {
                      window.location=sitequeuemanager.var.url+response.queueurl+"?session_key="+response['session_key'];
                  }
	    }
            setTimeout(function() { sitequeuemanager.check_queue(); },5000);
          },
          error: function(response){
            setTimeout(function() { sitequeuemanager.check_queue(); },20000);
          }
        });

     },
     getQueryParam: function(param, defaultValue = undefined) {
         location.search.substr(1)
             .split("&")
             .some(function(item) { // returns first occurence and stops
                 return item.split("=")[0] == param && (defaultValue = item.split("=")[1], true)
             })
         return defaultValue
     },
     createCookie: function(name, value, days) {
         var expires;
     
         if (days) {
             var date = new Date();
             date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
             expires = "; expires=" + date.toGMTString();
         } else {
             expires = "";
         }
         document.cookie = encodeURIComponent(name) + "=" + encodeURIComponent(value) + expires + "; path=/";
     },
     init: function() {

         if (window.jQuery) {
              var smactive = true;

              if ($('#site_queue_manager_active').length > 0) {
                    var site_queue_manager_active = $('#site_queue_manager_active').val();
                    if (site_queue_manager_active == 'disabled') {
	               smactive = false;
                    }
              }

              if (smactive == true) { 
                  if ($('#site_queue_frame').length == 0) { 
                     $('html').append('<div id="site_queue_frame" style="display:none;"> IFRAME</div>');
                  }
                  session_key = sitequeuemanager.getQueryParam('session_key');
                  if (session_key != undefined || session_key !=null) {
                      sitequeuemanager.createCookie('session_key',session_key,1)
                      sitequeuemanager.createCookie('sitequeuesession',session_key,30)
                      sitequeuemanager.var.session_key = session_key
                      $('#site_queue_frame').html('<iframe src="'+sitequeuemanager.var.url+"/site-queue/set-session/?session_key="+session_key+'" title="Set Session"></iframe>');
	          }
                  if ("parkstayUrl" in window) {
	                sitequeuemanager.var.url = parkstayUrl;
	          }

                  // if (window.jQuery) {
                  //     // jQuery is loaded
                  // } else {

                  //       var scriptTag = document.createElement('script');
                  //       scriptTag.src = sitequeuemanager.var.url+'/static/js/django_queue_manager/jquery-3.5.1.js';
                  //       //scriptTag.onload = "sitequeuemanager.check_queue();";
                  //       document.head.appendChild(scriptTag);
                  //       setTimeout(function() { sitequeuemanager.init();}, 200);
                  //     // jQuery is not loaded
                  //  //   alert("Doesn't Work");
                  // }

                  if (window.jQuery) {
                      sitequeuemanager.var.queueurl = 'false';
                      if ($("#queue").length> 0) {
                            var queue = $("#queue").val();
                            if (queue == 'true') {
                               sitequeuemanager.var.queueurl = 'true';
                            }
                      }
                      if (sitequeuemanager.var.running == 'false' ) {
                         sitequeuemanager.check_queue();
                      }
                  }
              }
          } else {
                 var scriptTag = document.createElement('script');
                 scriptTag.src = sitequeuemanager.var.url+'/static/js/django_queue_manager/jquery-3.5.1.js';
                 //scriptTag.onload = "sitequeuemanager.check_queue();";
                 document.head.appendChild(scriptTag);
                 setTimeout(function() { sitequeuemanager.init();}, 200);
	  }

     }

}
sitequeuemanager.init();
