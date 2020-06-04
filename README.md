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


# TODO

Add 

INSTALLED_APPS needs to append 'django_site_queue'

Add JS
<script src="/static/js/django_queue_manager/site-queue-manager.js"></script>

Add Environment vairables above
