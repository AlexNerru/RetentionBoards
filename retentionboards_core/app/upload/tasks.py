from __future__ import absolute_import, unicode_literals
from celery import task
from celery import shared_task
from retentionboards_core.celerymanager import app

@shared_task
def hello():
    return "Hello"

@shared_task
def publish_message(message):
    with app.producer_pool.acquire(block=True) as producer:
        producer.publish(
            message,
            exchange='retention_exchange',
            routing_key='key',
        )