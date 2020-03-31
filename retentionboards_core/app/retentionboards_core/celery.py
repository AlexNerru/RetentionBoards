import os
from celery import Celery, bootsteps
import kombu
from time import sleep

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retentionboards_core.settings')

app = Celery('retentionboards_core')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

with app.pool.acquire(block=True) as conn:
    exchange = kombu.Exchange(
        name='retention_exchange',
        type='direct',
        durable=True,
        channel=conn,
    )
    exchange.declare()
    queue = kombu.Queue(
        name='retention_queue',
        exchange=exchange,
        routing_key='key',
        channel=conn,
        message_ttl=600,
        queue_arguments={
            'x-queue-type': 'classic'
        },
        durable=True
    )
    queue.declare()

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))