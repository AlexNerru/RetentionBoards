from __future__ import absolute_import, unicode_literals

import os
from celery import Celery
from kombu import Exchange, Queue

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retentionboards_core.settings')

app = Celery('retentionboards_core')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

priority_to_routing_key = {'high': 'hipri',
                           'mid': 'midpri',
                           'low': 'lopri'}

with app.pool.acquire(block=True) as conn:

    exchange = Exchange(name='retention_exchange', type='direct', durable=True, channel=conn)

    exchange.declare()


def send_as_message(message, priority='mid'):
    routing_key = priority_to_routing_key[priority]
    with app.producer_pool.acquire(block=True) as publisher:
        publisher.publish(message,
                          serializer='json',
                          exchange=exchange,
                          declare=[exchange],
                          routing_key=routing_key)

