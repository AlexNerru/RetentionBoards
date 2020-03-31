from __future__ import absolute_import, unicode_literals

import os
from celery import Celery, bootsteps
from kombu import Exchange, Queue, Consumer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retentionboards_retentioneering.settings')

app = Celery('retentionboards_retentioneering')
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


class MyConsumerStep(bootsteps.ConsumerStep):

    def get_consumers(self, channel):
        return [Consumer(channel,
                         queues=[queue_hi, queue_mid, queue_lo],
                         callbacks=[self.handle_message],
                         accept=['json'])]

    def process_task(self, body, message):
        fun = body['fun']
        args = body['args']
        kwargs = body['kwargs']
        try:
            fun(*args, **kwargs)
        except Exception as exc:
            print("Error")
        message.ack()

    def handle_message(self, body, message):
        print('Received message: {0!r}'.format(body))
        message.ack()


app.steps['consumer'].add(MyConsumerStep)
