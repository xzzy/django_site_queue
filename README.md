# django_site_queue 
This is a django plugin that will monitor CPU and limit the number of people navigating your 
website by placing users into a waiting room allowing you to preserve resourses reducing the server 
load and bottleneck.

# Requirements

- Python (3.x.x)
- Python (2.7.x)
- PostgreSQL (>=9.3)
- Django (>=1.11.x)

# settings.py

These below environment vairables should be added to your settings.py or .env so you can configure the queue system for the load of your site.

    SESSION_TOTAL_LIMIT=2
    SESSION_LIMIT_SECONDS=45
    CPU_PERCENTAGE_LIMIT=50
    IDLE_LIMIT_SECONDS=25
    ACTIVE_SESSION_URL="/"
    WAITING_QUEUE_ENABLED="True"
    QUEUE_GROUP_NAME="site1"


# Explaining environment vairables
SESSION_TOTAL_LIMIT = Total active slots before session are queued in the waiting queue.
SESSION_LIMIT_SECONDS = Total time on site before being placed back into the queue
CPU_PERCENTAGE_LIMIT = When the CPU reaches a percentage limit session will be placed in the waiting queue until the cpu usage drops below.   This overrides SESSION_TOTAL_LIMIT
IDLE_LIMIT_SECONDS = This is the amount of time in seconds the user hasn't pinged the queue before we consider the user no longer on the site.
ACTIVE_SESSION_URL= When a slot has been allocated and the user has been waiting in the queue this is the URL the user is redirected to.
WAITING_QUEUE_ENABLED= True=Enable queuing ,  False=Disables Queue
QUEUE_GROUP_NAME=If you have multple sites sharing the same database you can use unique group names eg, site1 , site2 etc.  (Each group with limit based on the environment variables above)


# TODO

Add 

INSTALLED_APPS needs to append 'django_site_queue'

Add JS
<script src="/static/js/django_queue_manager/site-queue-manager.js"></script>

Add Environment vairables above
