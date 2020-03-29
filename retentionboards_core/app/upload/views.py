from django.http import HttpResponse
from django.views import View
from django.shortcuts import render, redirect
from django.contrib import messages

from .tasks import publish_message
from events.models import EventSet, Event

import logging
import csv, io

logger = logging.getLogger('django')
request_logger = logging.getLogger('django.request')

def my_pub_view(request):
    publish_message({'hello': 'world'})
    return HttpResponse(status=201)


class UploadView(View):
    template = "upload_csv.html"

    def get(self, request):
        if request.user.is_authenticated:
            return render(request, self.template)
        else:
            return redirect('/web/app/')


    def post(self, request):
        if request.user.is_authenticated:
            csv_file = request.FILES['file']
            if not csv_file.name.endswith('.csv'):
                messages.error(request, 'THIS IS NOT A CSV FILE')
            data_set = csv_file.read().decode('UTF-8')

            io_string = io.StringIO(data_set)
            next(io_string)

            eventset, _ = EventSet.objects.update_or_create(name=csv_file.name[:-4], user=request.user)

            print(type(eventset))
            event_list = []
            for column in csv.reader(io_string, delimiter=',', quotechar="|"):
                event = Event (
                    event_name=column[0],
                    event_timestamp=column[1],
                    user_pseudo_id=column[2],
                    event_set=eventset
                )
                event_list.append(event)
            Event.objects.bulk_create(event_list)
            publish_message({'hello': 'world'})
            return redirect('/web/app/')
        else:
            return redirect('/web/app/')


