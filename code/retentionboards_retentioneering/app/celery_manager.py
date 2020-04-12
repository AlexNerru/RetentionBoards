from __future__ import absolute_import, unicode_literals

import os
from celery import Celery
from kombu import Queue

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'retentionboards_retentioneering.settings')

app = Celery('retentionboards_retentioneering')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(['analytics.tasks', 'retentionboards_retentioneering.tasks'],
                       force=True)

with app.connection_or_acquire(block=True) as conn:

    queue_hi = Queue(name='retention_queue_hi', exchange='retention_exchange', routing_key='hipri', message_ttl=600,
                     durable=True, channel=conn)
    queue_mid = Queue(name='retention_queue_mid', exchange='retention_exchange', routing_key='midpri', message_ttl=600,
                      durable=True, channel=conn)
    queue_lo = Queue(name='retention_queue_lo', exchange='retention_exchange', routing_key='lopri', message_ttl=600,
                     durable=True, channel=conn)

    queues = [queue_hi, queue_mid, queue_lo]

    app.conf.task_queues = queues
