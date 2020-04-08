from __future__ import absolute_import, unicode_literals

import pandas as pd

from retentioneering_library.visualization.plot import step_matrix
from retentioneering_library.core.utils import init_config

from time import sleep

import psycopg2
from psycopg2.extras import RealDictCursor

import os

from celery import shared_task, current_task
from celery import states

from .redis_connector import save_image_to_redis

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
        from dashboards_event
        where event_set_id = {}
        order by event_timestamp"""


@shared_task(name='prepare_dataset')
def prepare_dataset(eventset_id):
    current_task.update_state(state=states.STARTED)

    init_config(
        experiments_folder='experiments',
        index_col='user_pseudo_id',  # column by which we split users / sessions / whatever
        event_col='event_name',  # column that describes event
        event_time_col='event_timestamp',  # column that describes timestamp of event
        positive_target_event='lost',  # name of positive target event
        negative_target_event='passed',  # name of negative target event
        pos_target_definition={
            # how to define positive event, e.g. empty means that add passed for whom was not 'lost'
            'time_limit': 600
        },
        neg_target_definition={  # how to define negative event, e.g. users who were inactive for 600 seconds.

        },
    )

    data = pd.read_sql_query(query_string.format(eventset_id), con=conn)
    data = data.sort_values('event_timestamp')

    desc_table = data.retention.get_step_matrix(max_steps=30, plot_type=False)
    heatmap = step_matrix(
        desc_table.round(2),
        title='Step matrix')
    save_image_to_redis(eventset_id, 'heatmap', heatmap[0])
    sleep(10)
    return eventset_id