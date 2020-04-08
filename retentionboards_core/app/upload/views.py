from django.views import View
from django.shortcuts import render, redirect
from django.contrib import messages

from dashboards.models import EventSet, Event
from .forms import UploadForm

import logging
import csv, io

from celery_manager import app as celery_app
from celery import states
from celery.result import AsyncResult

import pickle
from redis import Redis

logger = logging.getLogger('django')
request_logger = logging.getLogger('django.request')


class UploadView(View):
    template = "dashboard.html"

    def post(self, request):
        if request.user.is_authenticated:
            form = UploadForm(request.POST, request.FILES)
            if form.is_valid():
                csv_file = request.FILES['file']
                if not csv_file.name.endswith('.csv'):
                    messages.error(request, 'THIS IS NOT A CSV FILE')
                data_set = csv_file.read().decode('UTF-8')

                io_string = io.StringIO(data_set)
                next(io_string)

                eventset, _ = EventSet.objects.update_or_create(name=csv_file.name[:-4], user=request.user)

                event_list = []
                for column in csv.reader(io_string, delimiter=',', quotechar="|"):
                    event = Event(
                        event_name=column[0],
                        event_timestamp=column[1],
                        user_pseudo_id=column[2],
                        event_set=eventset
                    )
                    event_list.append(event)
                Event.objects.bulk_create(event_list)

                data = celery_app.send_task(name='prepare_dataset', args=[eventset.id], queue='retention_queue_hi')

                #print(data.result)
                redis = Redis(host='redis_queue', port=6379)
                #print(type(redis.get(data.result)))
                #print(type(pickle.loads(redis.get(data.result))))

                return render(request, self.template, {'eventsets': [[eventset]], 'task_id':data})
            else:
                messages.error(request, 'FORM IS NOT VALID')
                return redirect('/web/app/dashboard/')
        else:
            messages.error(request, 'USER IS NOT AUTHENTICATED')
            return redirect('/web/app/')
