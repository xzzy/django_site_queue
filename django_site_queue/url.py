from django.conf.urls import url
from django_crispy_jcaptcha import views

urlpatterns = [
    url(r'^site-queue-manager/$', views.QueuePage, name='site-queue-manager'),
]
