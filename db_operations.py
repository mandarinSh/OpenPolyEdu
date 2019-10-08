from store import *


def create_event_table(connection):
    create_table_query = '''
        CREATE TABLE event_types
        (ID BIGSERIAL PRIMARY KEY,
        EVENT_TYPE TEXT NOT NULL,
        EVENT TEXT NOT NULL)'''
    execute_query(connection, create_table_query)


def create_clicked_events_table(connection):
    create_table_query = '''
        CREATE TABLE clicked_events
        (ID BIGSERIAL PRIMARY KEY,
        EVENT_TYPE TEXT NOT NULL,
        EVENT TEXT NOT NULL)'''
    execute_query(connection, create_table_query)


def create_timed_clicked_events_table(connection):
    create_table_query = '''
        CREATE TABLE clicked_timed_events
        (ID BIGSERIAL PRIMARY KEY,
        EVENT_TYPE TEXT NOT NULL,
        EVENT TEXT NOT NULL,
        TIME TEXT NOT NULL)'''
    execute_query(connection, create_table_query)


def create_event_field_table(connection, table):
    create_table_query = """
            CREATE TABLE {table}
            (ID BIGSERIAL PRIMARY KEY,
            EVENT_TYPE TEXT NOT NULL,
            EVENT TEXT NOT NULL,
            TIME TEXT NOT NULL)""".format(table=table)
    execute_query(connection, create_table_query)


def insert_events(connection, event, event_type):
    insert_event_query = """INSERT INTO event_types
        (EVENT_TYPE, EVENT) VALUES ('{event_type}', '{event}');""".\
        format(event=event, event_type=event_type)

    execute_query(connection, insert_event_query)


def insert_clicked_events(connection, event, event_type):
    insert_event_query = """INSERT INTO clicked_events
        (EVENT_TYPE, EVENT) VALUES ('{event_type}', '{event}');""".\
        format(event=event, event_type=event_type)

    execute_query(connection, insert_event_query)


def insert_clicked_events_time(connection, event, event_type, time):
    insert_event_query = """INSERT INTO clicked_timed_events
        (EVENT_TYPE, EVENT, TIME) VALUES ('{event_type}', '{event}', '{time}');""".\
        format(event=event, event_type=event_type, time=time)

    execute_query(connection, insert_event_query)


def insert_event_field_events(connection, event, event_type, time, table):
    insert_event_query = """INSERT INTO {table}
        (EVENT_TYPE, EVENT, TIME) VALUES ('{event_type}', '{event}', '{time}');""".\
        format(table=table, event=event, event_type=event_type, time=time)

    execute_query(connection, insert_event_query)
