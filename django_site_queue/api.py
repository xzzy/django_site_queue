import traceback
import base64
import json
from six.moves.urllib.parse import urlparse
from wsgiref.util import FileWrapper
from django.db import connection, transaction
from django.db.models import Q, Min
from django.http import HttpResponse
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError
from django.conf import settings
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django_site_queue import models
from django.utils.crypto import get_random_string
from datetime import datetime, timedelta
from django.utils import timezone
import psutil


# NOTE
# Add Internal User login check and ignore staff membbers from queue checks
# Add CPU Checks
# Improve queue algorithm

def check_create_session(request, *args, **kwargs):
    try:
        sitequeuesession = None
        sitesession = None
        session_total_limit = 1
        session_limit_seconds = 35 

        idle_limit_seconds = 60
        idle_seconds = 3000
        session_count = 0
        total_active_session = models.SiteQueueManager.objects.filter(status=1, expiry__gte=datetime.now(timezone.utc)).count()
        total_waiting_session = models.SiteQueueManager.objects.filter(status=0, expiry__gte=datetime.now(timezone.utc)).count()
        print (psutil.cpu_percent(interval=None))
        #print (psutil.cpu_percent(interval=1, percpu=True)) 
        #print (psutil.cpu_percent(interval=1))        
        #request.session['sitequeuesession'] = None 
        if 'sitequeuesession' in request.session:
             sitequeuesession = request.session['sitequeuesession']
             session_count = models.SiteQueueManager.objects.filter(session_key=sitequeuesession,expiry__gte=datetime.now(timezone.utc)).count()

        #print ("SITESESSION")
        #print (sitequeuesession)

        if sitequeuesession is None or session_count == 0:
            session_status = 1
            if total_active_session >= session_total_limit:
                session_status = 0
 
            session_key = get_random_string(length=60, allowed_chars=u'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
            expiry=datetime.now(timezone.utc)+timedelta(seconds=session_limit_seconds)
            sitesession = models.SiteQueueManager.objects.create(session_key=session_key,idle=datetime.now(timezone.utc), expiry=expiry,status=session_status,ipaddress=get_client_ip(request))
            request.session['sitequeuesession'] = session_key
        else:
            if models.SiteQueueManager.objects.filter(session_key=sitequeuesession).count() > 0:
                 sitesession_query = models.SiteQueueManager.objects.filter(session_key=sitequeuesession)
                 sitesession = sitesession_query[0]
                 # check if expired and create new one below
                 
                 if total_active_session < session_total_limit and sitesession.status != 1:
                        session_status = 1
                        sitesession.status = session_status
                        sitesession.expiry = datetime.now(timezone.utc)+timedelta(seconds=session_limit_seconds)


                 sitesession.idle=datetime.now(timezone.utc)
                 sitesession.save()
            else:
                 raise ValidationError("Error no session Found")

        idle_seconds = (datetime.now(timezone.utc)-sitesession.idle).seconds
        expiry_seconds = (sitesession.expiry-datetime.now(timezone.utc)).seconds
        if expiry_seconds < 1:
              request.session['sitequeuesession'] = None
              if total_active_session < session_total_limit:
                  sitesession.status = 1
                  sitesession.expiry = datetime.now(timezone.utc)+timedelta(seconds=session_limit_seconds)
              else:
                  sitesession.status = 0
                  sitesession.expiry = datetime.now(timezone.utc)
              sitesession.save() 

        #if idle_limit_seconds > idle_seconds and sitesession.status == 1:
        #booking = utils.get_session_booking(request.session)
        #request.session['sitequeuesession'] = "ThisisaQueueSession"

    except Exception as e:
        print (e)
        pass

    return HttpResponse(json.dumps({'url':'/map/', 'queueurl': '/site-queue/view/','session': request.session['sitequeuesession'], 'idle_seconds':idle_seconds,'expiry': sitesession.expiry.strftime('%d/%m/%Y %H:%M'), 'idle': sitesession.idle.strftime('%d/%m/%Y %H:%M'),'status': models.SiteQueueManager.QUEUE_STATUS[sitesession.status][1],'total_active_session': total_active_session, 'total_waiting_session': total_waiting_session,'expiry_seconds': expiry_seconds}), content_type='application/json')

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
       ip = x_forwarded_for.split(',')[-1].strip()
    else:
       ip = request.META.get('REMOTE_ADDR')
    return ip


#
#    session_key = models.CharField(max_length=256)
#    idle = models.DateTimeField(blank=True, null=True)
#    expiry = models.DateTimeField(blank=True, null=True)
#    status = models.SmallIntegerField(choices=QUEUE_STATUS, default=0)
#    ipaddress = models.CharField(max_length=100)
#    created = models.DateTimeField(auto_now_add=True, editable=False)
#
