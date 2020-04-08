from __future__ import absolute_import, unicode_literals
from celery import shared_task
from time import sleep

from celery_manager import app


'''@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(60.0, send_ping.s('hello'), name='ping', options={'routing_key': 'task'})


@shared_task(name='ping')
def send_ping(message="hello world"):
    sleep(5)
    print(message)'''
