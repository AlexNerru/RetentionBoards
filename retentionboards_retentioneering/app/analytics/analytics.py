import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
import os

conn = psycopg2.connect(
    database='hello_django_dev',
    host='db',
    port='5432',
    user=os.environ.get("SQL_USER", "user"),
    password=os.environ.get("SQL_PASSWORD", "password"),
    cursor_factory=RealDictCursor
)

def prepare_dataset(eventset_id):
    query_string = f"""
        select
            event_name as event_name,
            event_timestamp as event_timestamp,
            user_pseudo_id as user_pseudo_id
        from events_event
        where event_set_id = {eventset_id}
        order by event_timestamp"""

    df = pd.read_sql_query(query_string, con=conn)
    print ("sucess")

