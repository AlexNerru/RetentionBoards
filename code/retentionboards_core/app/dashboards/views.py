from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt

from dashboards.models import EventSet, Event, EventsetStatus
from dashboards.forms import UploadForm

from celery.result import AsyncResult
from celery_manager import app as celery_app

from redis import Redis

import csv, io
import logging
import json
import os
import pickle
from PIL import Image

logger = logging.getLogger('django')
request_logger = logging.getLogger('django.request')


class EventsetsView(View):
    template = "dashboard.html"

    def get(self, request):
        if request.user.is_authenticated:
            form = UploadForm()

            eventsets_list = EventSet.get_eventset_list(user=request.user)

            return render(request, self.template, {'eventsets': eventsets_list, 'form': form})
        else:
            messages.error(request, 'USER IS NOT AUTHENTICATED')
            return redirect('/web/app/')

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

                eventset, _ = EventSet.objects.update_or_create(name=form.data['name'], user=request.user,
                                                                status=EventsetStatus.NEW)

                print(eventset.id)
                event_list = []
                users = set()
                unique_events = set()
                for column in csv.reader(io_string, delimiter=',', quotechar="|"):
                    users.add(column[2])
                    unique_events.add(column[0])
                    event = Event(
                        event_name=column[0],
                        event_timestamp=column[1],
                        user_pseudo_id=column[2],
                        event_set=eventset
                    )
                    event_list.append(event)

                eventset.events = len(event_list)
                eventset.users = len(users)
                eventset.unique_events=len(unique_events)
                Event.objects.bulk_create(event_list)

                task_id = celery_app.send_task(name='prepare_dataset', args=[eventset.id], queue='retention_queue_hi')
                task_tsne = celery_app.send_task(name='learn_tsne', args=[eventset.id], queue='retention_queue_hi')

                eventset.step_matrix_task_id = task_id
                eventset.tsne_task_id = task_tsne

                eventset.save()

                eventsets_list = EventSet.get_eventset_list(user=request.user)

                form = UploadForm()

                return render(request, self.template, {'eventsets': eventsets_list, 'task_id': task_id, 'task_tsne':
                                                        task_tsne, 'eventset_name': eventset.name, 'form': form})
            else:
                messages.error(request, 'FORM IS NOT VALID')
                return redirect('/web/app/dashboard/')
        else:
            messages.error(request, 'USER IS NOT AUTHENTICATED')
            return redirect('/web/app/')


class ExperimentView(View):
    template = 'experiment.html'

    def get(self, request, pk):
        request_logger.debug(request)
        if request.user.is_authenticated:
            #if request.user.has_perm('crud portfolio', portfolio):

            redis = Redis(host=os.environ.get("REDIS_HOST", 'redis'), port=os.environ.get("REDIS_PORT", 6379))

            eventset = get_object_or_404(EventSet, pk=pk)
            task_id = eventset.step_matrix_task_id
            task_tsne = eventset.tsne_task_id

            step_matrix_link = f'images/experiments/step_matrix/file{pk}.png'
            if AsyncResult(task_id).result is not None:
                step_matrix = pickle.loads(redis.get('heatmap' + str(pk)))
                step_matrix.save('staticfiles/' + step_matrix_link)

            tsne_link = f'images/experiments/tsne/file{pk}.png'
            if AsyncResult(task_tsne).result is not None:
                tsne = pickle.loads(redis.get('tsne' + str(pk)))
                tsne.save('staticfiles/' + tsne_link)

            graph = None
            graphs_all = []

            if AsyncResult(task_tsne).result is not None:
                for cluster in AsyncResult(task_tsne).result[1]:
                    graph = pickle.loads(redis.get(cluster))
                    with open(f'staticfiles/images/experiments/graphs/{cluster}.html', 'w+') as f:
                        f.write(graph)
                    graphs_all.append([f'/web/app/dashboard/experiments/{pk}/{cluster}/', cluster])

            return render(request, self.template,  {'eventset': eventset, 'tsne_link': tsne_link,
                                                        'step_matrix_link': step_matrix_link, 'graphs_all': graphs_all})
                #else:
                #    portfolios = Portfolio.objects.filter(user=request.user.profile).all()
                #    portfolio_list = get_portfolios_list(portfolios=portfolios)
                #    messages.add_message(request, messages.ERROR, 'You do not have access to this portfolio')
                #    return render(request, 'portfolios_list.html', {'list': portfolio_list})
        else:
            messages.add_message(request, messages.ERROR, 'You are not authentificated')
            return redirect('/web/app/')

class GraphView(View):
    template = "graph.html"

    def get(self, request, pk, cluster):
        if request.user.is_authenticated:
            with open(f'staticfiles/images/experiments/graphs/{cluster}.html', 'r') as f:
                graph = f.read()
            return render(request, self.template, {'graph': graph})
        else:
            messages.error(request, 'USER IS NOT AUTHENTICATED')
            return redirect('/web/app/')


@csrf_exempt
def check_task_status(request):
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
