import json
import sys
from store import *
from db_operations import *


# DB operations

def put_events_to_clicked_events(json_obj, connection):
    if json_obj["event_type"] != "" and isinstance(json_obj["event_type"], str) \
            and json_obj["event_type"] != '''{}'''\
            and ("click" in json_obj["event_type"] or "select" in json_obj["event_type"]):

        insert_clicked_events(connection, json_obj["event"], json_obj["event_type"])


def put_events_to_clicked_timed_events(json_obj, connection):
    if json_obj["event_type"] != "" and isinstance(json_obj["event_type"], str) \
            and json_obj["event_type"] != '''{}'''\
            and ("click" in json_obj["event_type"] or "select" in json_obj["event_type"]):

        insert_clicked_events_time(connection, json_obj["event"], json_obj["event_type"], json_obj["time"])


def put_event_field_events(json_obj, connection, table, e_type):
    count = 0

    if e_type in json_obj["event_type"]:
        insert_event_field_events(
            connection,
            json_obj["event"],
            json_obj["event_type"],
            json_obj["time"],
            table)
        count = 1

    return count


def count_time():
    pass
