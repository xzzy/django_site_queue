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
from confy import env
from django.core.urlresolvers import reverse
import psutil

# NOTE
# Add Internal User login check and ignore staff membbers from queue checks - DONE
# Add CPU Checks DONE
# Delete old sessions idle and expired - DONE
# Create ENVIRONMENT VAIRABLES DONE
# Disable Option for DEV DONE
# inject into map screen DONE
# README DONE

# Improve queue algorithm - more work on queue order

def check_create_session(request, *args, **kwargs):
    
    sitequeuesession = None
    sitesession = None
    session_total_limit = int(env('SESSION_TOTAL_LIMIT', 2))
    session_limit_seconds = int(env('SESSION_LIMIT_SECONDS', 20))
    cpu_percentage_limit = int(env('CPU_PERCENTAGE_LIMIT', 10))
    idle_limit_seconds = int(env('IDLE_LIMIT_SECONDS', 15))
    active_session_url = env('ACTIVE_SESSION_URL', "/")
    waiting_queue_enabled = env('WAITING_QUEUE_ENABLED','False') 
    queue_group_name = env('QUEUE_GROUP_NAME','default')

    idle_seconds = 3000
    session_count = 0
    staff_loggedin = False
     
    session_key = '' 

    try:
        if 'session_key' in request.COOKIES:
             session_key = request.COOKIES.get('sitequeuesession','')
             request.session['sitequeuesession'] = session_key
        if 'session_key' in request.GET:
            if len(request.GET['session_key']) > 10: 
            #session_key = request.COOKIES['sitequeuesession']
                 session_key = request.GET['session_key']
                 request.session['sitequeuesession'] = session_key
 
        #print (request.session['sitequeuesession'])

        # Clean up stale sessions
        idle_dt_subtract = datetime.now(timezone.utc)-timedelta(seconds=idle_limit_seconds)
        models.SiteQueueManager.objects.filter(expiry__lte=datetime.now(timezone.utc), status=1, queue_group_name=queue_group_name).delete()
        models.SiteQueueManager.objects.filter(idle__lte=idle_dt_subtract, queue_group_name=queue_group_name).delete()
        if request.user.is_authenticated:
             if request.user.is_staff is True:
                   staff_loggedin = True
         
        total_active_session = models.SiteQueueManager.objects.filter(status=1, expiry__gte=datetime.now(timezone.utc),is_staff=False,queue_group_name=queue_group_name).count()
        total_waiting_session = models.SiteQueueManager.objects.filter(status=0, expiry__gte=datetime.now(timezone.utc),queue_group_name=queue_group_name).count()
        cpu_percentage = psutil.cpu_percent(interval=None)
        #print (cpu_percentage)
        if 'sitequeuesession' in request.session:
             sitequeuesession = request.session['sitequeuesession']
        else:
             request.session['sitequeuesession']  = None 

        #### 
        session_count = models.SiteQueueManager.objects.filter(session_key=sitequeuesession,expiry__gte=datetime.now(timezone.utc),queue_group_name=queue_group_name).count()
        if sitequeuesession is None or session_count == 0:
            session_status = 0
            #if total_active_session >= session_total_limit:
            if total_active_session < session_total_limit and total_waiting_session == 0:
                  session_status = 1
            if cpu_percentage > cpu_percentage_limit:
                  session_status = 0
            if staff_loggedin is True:
                  session_status = 1
            #if session_key:
            #     pass
            #else: 
            session_key = get_random_string(length=60, allowed_chars=u'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
            expiry=datetime.now(timezone.utc)+timedelta(seconds=session_limit_seconds)
            sitesession = models.SiteQueueManager.objects.create(session_key=session_key,idle=datetime.now(timezone.utc), expiry=expiry,status=session_status,ipaddress=get_client_ip(request), is_staff=staff_loggedin,queue_group_name=queue_group_name)
            request.session['sitequeuesession'] = session_key
            request.COOKIES['sitequeuesession'] = session_key
        else:
            if models.SiteQueueManager.objects.filter(session_key=sitequeuesession).count() > 0:
                 sitesession_query = models.SiteQueueManager.objects.filter(session_key=sitequeuesession,queue_group_name=queue_group_name)
                 sitesession = sitesession_query[0]
                 # check if expired and create new one below
                 longest_waiting = models.SiteQueueManager.objects.filter(status=0, expiry__gte=datetime.now(timezone.utc),queue_group_name=queue_group_name).order_by('created')[:session_total_limit]
                 #print (longest_waiting)
                 if total_active_session < session_total_limit and sitesession.status != 1:
                       if cpu_percentage < cpu_percentage_limit:
                            for lw in longest_waiting:
                                if request.session['sitequeuesession'] == lw.session_key:
                                    session_status = 1
                                    sitesession.status = session_status
                                    sitesession.expiry = datetime.now(timezone.utc)+timedelta(seconds=session_limit_seconds)
                                else:
                                    sitesession.expiry = datetime.now(timezone.utc)+timedelta(seconds=session_limit_seconds)
                       else:
                           sitesession.expiry = datetime.now(timezone.utc)+timedelta(seconds=session_limit_seconds)

                 if sitesession.status == 0:
                        sitesession.expiry = datetime.now(timezone.utc)+timedelta(seconds=session_limit_seconds)
                 if staff_loggedin is True:
                        session_status = 1
                        sitesession.status = session_status
                        sitesession.expiry = datetime.now(timezone.utc)+timedelta(seconds=session_limit_seconds)
                        sitesession.is_staff=staff_loggedin

                 sitesession.idle=datetime.now(timezone.utc)
                 sitesession.save()
            else:
                 raise ValidationError("Error no session Found")

        idle_seconds = (datetime.now(timezone.utc)-sitesession.idle).seconds
        expiry_seconds = (sitesession.expiry-datetime.now(timezone.utc)).seconds
        #if expiry_seconds < 1:
        #      request.session['sitequeuesession'] = None
        #      if total_active_session <= session_total_limit and total_waiting_session == 0:
        #          sitesession.status = 1
        #          sitesession.expiry = datetime.now(timezone.utc)+timedelta(seconds=session_limit_seconds)
        #      else:
        #          sitesession.status = 0
        #          sitesession.expiry = datetime.now(timezone.utc)
        #      sitesession.save() 

        #if idle_limit_seconds > idle_seconds and sitesession.status == 1:
        #booking = utils.get_session_booking(request.session)
        #request.session['sitequeuesession'] = "ThisisaQueueSession"
    except Exception as e:
        print (e)
        pass
    if waiting_queue_enabled == False or waiting_queue_enabled == "False":
         sitesession.status = 1

    CORS_SITES = env('CORS_SITES', None)

    if settings.DEBUG is True:    
        response = HttpResponse(json.dumps({'url':active_session_url, 'queueurl': reverse('site-queue-page'),'session': request.session['sitequeuesession'], 'idle_seconds':idle_seconds,'expiry': sitesession.expiry.strftime('%d/%m/%Y %H:%M'), 'idle': sitesession.idle.strftime('%d/%m/%Y %H:%M'),'status': models.SiteQueueManager.QUEUE_STATUS[sitesession.status][1],'total_active_session': total_active_session, 'total_waiting_session': total_waiting_session,'expiry_seconds': expiry_seconds,'session_key': session_key }), content_type='application/json')
        if CORS_SITES:
            response["Access-Control-Allow-Origin"] = "*"
            response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
            response["Access-Control-Max-Age"] = "0"
            response["Access-Control-Allow-Headers"] = "*"
        response.set_cookie('sitequeuesession', session_key)
        return response
    else:
        response = HttpResponse(json.dumps({'url':active_session_url, 'queueurl': reverse('site-queue-page'),'status': models.SiteQueueManager.QUEUE_STATUS[sitesession.status][1],'session_key': session_key}), content_type='application/json')
        if CORS_SITES:
            response["Access-Control-Allow-Origin"] = "*" 
            response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
            response["Access-Control-Max-Age"] = "0"
            response["Access-Control-Allow-Headers"] = "*"
        response.set_cookie('sitequeuesession', session_key)
        return response

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
