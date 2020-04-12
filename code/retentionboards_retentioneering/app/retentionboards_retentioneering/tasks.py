from __future__ import absolute_import, unicode_literals
from celery import shared_task
from time import sleep


@shared_task(name='ping-pong')
def send_ping_pong(message="hello ping-pong"):
    sleep(15)
    print(message)


@shared_task(name='ping')
def send_ping(message, id):
    sleep(5)
    print(message)
    return (id)


@shared_task(name='pong')
def send_pong(message="hello pong"):
    sleep(10)
    print(message)