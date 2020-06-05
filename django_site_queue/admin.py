from django.contrib.gis import admin
from django.contrib.admin import AdminSite
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django_site_queue import models

@admin.register(models.SiteQueueManager)
class SiteQueueManagerClassAdmin(admin.ModelAdmin):
    list_display = ('id','idle','expiry','status','ipaddress','is_staff','created','session_key',)
    search_fields = ('ipaddress','session_key',)
    list_filter = ('ipaddress','status',)

