from __future__ import absolute_import, unicode_literals
from celery import shared_task
from time import sleep


@shared_task(name='ping')
def send_ping(message="hello world"):
    sleep(20)
    print(message)
