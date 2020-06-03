import logging
from django.db.models import Q
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.views.generic.base import View, TemplateView
from django.conf import settings
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie
from django import forms
from django.views.generic.base import View, TemplateView
from django.template.loader import get_template


class QueuePage(TemplateView):
    # preperation to replace old homepage with screen designs..

    template_name = 'site_queue/queue.html'
    def render_to_response(self, context):

        template = get_template(self.template_name)
        #context['csrf_token_value'] = get_token(self.request)
        return HttpResponse(template.render(context))

    def get_context_data(self, **kwargs):
        context = super(QueuePage, self).get_context_data(**kwargs)
        #context = template_context(self.request)
        #APP_TYPE_CHOICES = []
        #APP_TYPE_CHOICES_IDS = []
        return context
