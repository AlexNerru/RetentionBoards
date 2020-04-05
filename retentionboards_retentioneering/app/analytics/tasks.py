from __future__ import absolute_import, unicode_literals

import pandas as pd

from time import sleep

import psycopg2
from psycopg2.extras import RealDictCursor

import os

from celery import shared_task, current_task
from celery import states

conn = psycopg2.connect(
    database='hello_django_dev',
    host='db',
    port='5432',
    user=os.environ.get("SQL_USER", "user"),
    password=os.environ.get("SQL_PASSWORD", "password"),
    cursor_factory=RealDictCursor
)

query_string = """
        select
            event_name as event_name,
            event_timestamp as event_timestamp,
            user_pseudo_id as user_pseudo_id
        from events_event
        where event_set_id = {}
        order by event_timestamp"""

@shared_task(name = 'prepare_dataset')
def prepare_dataset(eventset_id):
    current_task.update_state(state=states.STARTED)
    df = pd.read_sql_query(query_string.format(eventset_id), con=conn)
    current_task.update_state(state=states.SUCCESS)

