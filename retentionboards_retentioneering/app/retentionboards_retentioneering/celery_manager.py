from __future__ import absolute_import, unicode_literals

import os
from time import sleep
from celery import Celery, bootsteps, shared_task
from kombu import Queue, Consumer
from analytics.analytics import prepare_dataset

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retentionboards_retentioneering.settings')

app = Celery('retentionboards_retentioneering')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

@shared_task(name='ping')
def send_ping(message="hello ping"):
    print(message)

@shared_task(name='pong')
def send_pong(message="hello pong"):
    sleep(10)
    print(message)

with app.connection_or_acquire(block=True) as conn:

    queue_hi = Queue(name='retention_queue_hi', exchange='retention_exchange', routing_key='hipri', message_ttl=600,
                     durable=True, channel=conn)
    queue_mid = Queue(name='retention_queue_mid', exchange='retention_exchange', routing_key='midpri', message_ttl=600,
                      durable=True, channel=conn)
    queue_lo = Queue(name='retention_queue_lo', exchange='retention_exchange', routing_key='lopri', message_ttl=600,
                     durable=True, channel=conn)

    queues = [queue_hi, queue_mid, queue_lo]

    app.conf.task_queues = queues

class MyConsumerStep(bootsteps.ConsumerStep):

    def get_consumers(self, channel):
        return [Consumer(channel, queue_mid,
                         callbacks=[self.process_next_task_mid],
                         accept=['json']),
                Consumer(channel, queue_hi,
                         callbacks=[self.process_next_task_high],
                         accept=['json'])]

    # @app.task(serializer='json', name='process-next-task')
    def process_next_task_high(self, body, message):
        print('Received message Task1: {0!r}'.format(body))
        prepare_dataset(1)
        message.ack()

    # @app.task(serializer='json', name='process-next-task')
    def process_next_task_mid(self, body, message):
        print('Received message Task2: {0!r}'.format(body))
        message.ack()


app.steps['consumer'].add(MyConsumerStep)
