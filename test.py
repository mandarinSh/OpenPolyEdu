import json
import sys
from store import *
from db_operations import *
from analysis import click_events
from analysis.click_events import *
import argparse


TAB_COUNT_EVENTS = '''tab_count_events'''
CLICK_EVENTS = '''click_events'''


def open_fh():
    fh = open('anonymized_logs.json', encoding="utf-8")
    return fh


def close_fh(fh):
    fh.close()


def put_events_to_event_types(json_obj, connection):
    if json_obj["event"] != "" and isinstance(json_obj["event"], str) \
            and json_obj["event"] != '''{"POST": {}, "GET": {}}''' \
            and json_obj["event"] != '''{}''':

        insert_events(connection, json_obj["event"], json_obj["event_type"])


def parse_log(fh, connection):
    count_selection_events = 0
    count_click_events = 0

    # create_event_field_table(connection, TAB_COUNT_EVENTS)
    # create_event_field_table(connection, CLICK_EVENTS)

    a = 50000
    b = 0

    while a != b:
        # while True:  # for reading the whole file
        line = fh.readline()
        if not line:
            break

        json_obj = json.loads(line)
        # print(line)
        # put_events_to_event_types(json_obj, connection)
        # put_events_to_clicked_events(json_obj, connection)
        # put_events_to_clicked_timed_events(json_obj, connection)

        count_selection_events += \
            put_event_field_events(json_obj, connection, TAB_COUNT_EVENTS, "select")
        count_click_events += \
            put_event_field_events(json_obj, connection, CLICK_EVENTS, "click")

        b += 1

    print("Count selection events: ")
    print(count_selection_events)

    print("Count clicked events: ")
    print(count_click_events)


def main(argv):
    parser = argparse.ArgumentParser()
    # parser.add_argument("-u", "--upgrade", help="fully automatized upgrade", action='store_true')
    parser.add_argument("-t", "--task", help="Number of task to run", choices=[0, 1, 2], type=int, action="store")
    # parser.add_argument("-h", "--help", required=False, help="1 - count total number of clicks")
    args = parser.parse_args()

    print(vars(args))

    fh = open_fh()
    connection = open_db_connection()
    # drop_table(connection, '''event_types''')
    drop_table(connection, TAB_COUNT_EVENTS)
    drop_table(connection, CLICK_EVENTS)
    # drop_table(connection, '''clicked_timed_events''')
    # drop_table(connection, '''tab_count_events''')

    create_event_field_table(connection, TAB_COUNT_EVENTS)
    create_event_field_table(connection, CLICK_EVENTS)
    # create_event_table(connection)
    # create_timed_clicked_events_table(connection)

    parse_log(fh, connection)

    close_fh(fh)


if __name__ == '__main__':
    main(sys.argv)
