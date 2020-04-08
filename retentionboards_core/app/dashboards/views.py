from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages

from .models import EventSet

from celery.result import AsyncResult
from upload.forms import UploadForm

import logging
import json

logger = logging.getLogger('django')
request_logger = logging.getLogger('django.request')


class EventsetsView(View):
    template = "dashboard.html"

    def get(self, request):
        if request.user.is_authenticated:
            form = UploadForm()
            return render(request, self.template, {'eventsets': [[]], 'form': form})
        else:
            messages.error(request, 'USER IS NOT AUTHENTICATED')
            return redirect('/web/app/')


class EventsetProcessingView(View):
    def post(self, request):

        if request.is_ajax():
            if 'task_id' in request.POST.keys() and request.POST['task_id']:
                task_id = request.POST['task_id']
                task = AsyncResult(task_id)
                data = task.state
            else:
                data = 'No task_id in the request'
        else:
            data = 'This is not an ajax request'
        json_data = json.dumps(data)
        return HttpResponse(json_data, content_type='application/json')
