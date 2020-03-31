'''from kombu import Connection, Exchange, Queue
from kombu.common import maybe_declare
from kombu.mixins import ConsumerMixin
from kombu.pools import producers
from kombu.utils.debug import setup_logging


connection_string = "redis://redis_queue:6379/"
priority_to_routing_key = {'high': 'hipri',
                           'mid': 'midpri',
                           'low': 'lopri'}

task_exchange = Exchange('tasks', type='direct')
task_queues = [Queue('hipri', task_exchange, routing_key='hipri'),
               Queue('midpri', task_exchange, routing_key='midpri'),
               Queue('lopri', task_exchange, routing_key='lopri')]

'''