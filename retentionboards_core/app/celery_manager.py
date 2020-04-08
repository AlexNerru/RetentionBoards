from __future__ import absolute_import, unicode_literals

import os
from celery import Celery
from kombu import Exchange, Queue

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retentionboards_core.settings')

app = Celery('retentionboards_core')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(['retentionboards_core.tasks'], force=True)

priority_to_routing_key = {'high': 'hipri',
                           'mid': 'midpri',
                           'low': 'lopri'}

with app.pool.acquire(block=True) as conn:

    exchange = Exchange(name='retention_exchange', type='direct', durable=True, channel=conn)

    queue_task = Queue(name='retention_queue_task', exchange='retention_exchange', routing_key='task', message_ttl=600,
                     durable=True, channel=conn)

    app.conf.task_queues=[queue_task]

    app.conf.task_default_exchange = 'retention_exchange'
    app.conf.task_default_exchange_type = 'direct'
    app.conf.task_default_routing_key = 'task'




