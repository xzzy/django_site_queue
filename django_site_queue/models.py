from __future__ import unicode_literals
from datetime import timedelta
from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.postgres.fields import JSONField
from django.core.urlresolvers import reverse
#from django.utils.encoding import python_2_unicode_compatible
#from model_utils import Choices
from django.contrib.auth.models import Group
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import ValidationError

#@python_2_unicode_compatible
class SiteQueueManager(models.Model):

    QUEUE_STATUS = (
        (0, 'Waiting'),        # not used
        (1, 'Active'),
    )

    session_key = models.CharField(max_length=256)
    idle = models.DateTimeField(blank=True, null=True)
    expiry = models.DateTimeField(blank=True, null=True)
    status = models.SmallIntegerField(choices=QUEUE_STATUS, default=0)
    ipaddress = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True, editable=False)

    def __str__(self):
        return self.session_key

