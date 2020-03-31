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
    exchange = Exchange(
        name='retention_exchange',
        type='direct',
        durable=True,
        channel=conn,
    )

    queue_hi = Queue(
        name='retention_queue_hi',
        exchange=exchange,
        routing_key='hipri',
        channel=conn,
        message_ttl=600,
        durable=True
    )

    queue_mid = Queue(
        name='retention_queue_mid',
        exchange=exchange,
        routing_key='midpri',
        channel=conn,
        message_ttl=600,
        durable=True
    )

    queue_lo = Queue(
        name='retention_queue_lo',
        exchange=exchange,
        routing_key='lopri',
        channel=conn,
        message_ttl=600,
        durable=True
    )


def send_as_message(message, priority='mid'):
    routing_key = priority_to_routing_key[priority]
    with app.producer_pool.acquire(block=True) as publisher:
        publisher.publish(message,
                          serializer='json',
                          exchange=exchange,
                          declare=[exchange, queue_hi, queue_mid, queue_lo],
                          routing_key=routing_key)


def send_as_task(fun, args=(), kwargs={}, priority='mid'):
    payload = {'fun': fun, 'args': args, 'kwargs': kwargs}
    routing_key = priority_to_routing_key[priority]

    with app.producer_pool.acquire(block=True) as publisher:
        publisher.publish(payload,
                          serializer='pickle',
                          compression='bzip2',
                          exchange=exchange,
                          declare=[exchange, queue_hi, queue_mid, queue_lo],
                          routing_key=routing_key)
