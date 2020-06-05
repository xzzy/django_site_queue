var sitequeuemanager  = { 
     var: {
        'queueurl': 'false',
        'running': 'false',
        'url': '',
     },
     check_queue: function() {
        sitequeuemanager.var.running = 'true';

        $.ajax({
          url: sitequeuemanager.var.url+'/api/check-create-session/',
          type: 'GET',
          data: {},
          cache: false,
          success: function(response) { 
            if (response.status == "Active")  {
                  if (sitequeuemanager.var.queueurl == 'true') { 
                      window.location=response.url;
                  }
	    } else {
                  if (sitequeuemanager.var.queueurl == 'true') {
                  } else {
                      window.location=response.queueurl;
                  }
	    }
            setTimeout(function() { sitequeuemanager.check_queue(); },5000);
          },
          error: function(response){
            setTimeout(function() { sitequeuemanager.check_queue(); },20000);
          }
        });

     },
     init: function() {
          if (parkstayUrl) { 
		sitequeuemanager.var.url = parkstayUrl;
	  }

          if (window.jQuery) {
              // jQuery is loaded
          } else {

                var scriptTag = document.createElement('script');
                scriptTag.src = '/static/js/django_queue_manager/jquery-3.5.1.js';
                //scriptTag.onload = "sitequeuemanager.check_queue();";
                document.head.appendChild(scriptTag);
                setTimeout(function() { sitequeuemanager.init();}, 200);
              // jQuery is not loaded
           //   alert("Doesn't Work");
          }

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

}
sitequeuemanager.init();
