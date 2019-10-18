import sys
import datetime
import csv
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from database_services import *


def calculate_events_distribution_per_day(connection):
    print('Start query execution at ', datetime.datetime.now())

    get_distribution_events = '''select 
            log_line ->> 'name' as event_name,
            TO_DATE(log_line ->> 'time', 'YYYY-MM-DD"T"HH24:MI:SS') as time_run,
            count (*) as count_of_start
        from logs
        where log_line ->> 'name' != ''
        group by time_run, event_name
        order by event_name'''

    connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = connection.cursor()
    cursor.execute(get_distribution_events)
    events_distribution = cursor.fetchall()
    cursor.close()
    connection.commit()

    print('End query execution at ', datetime.datetime.now())
    print("Events distribution per day has been calculated")
    return events_distribution


def write_result_to_file(result_file, result):
    print("Writing results to file")
    with open(result_file, mode='w') as res_file:
        field_names = ['time', 'event_name', 'count']
        result_file_writer = csv.writer(res_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        result_file_writer.writerow(field_names)
        for res in result:
            result_file_writer.writerow(res)


def generate_figure(event_distribution):
    print("Start figures generation...")
    events_dict = dict()
    for event in event_distribution:
        event_name = event[0]
        dates = events_dict.get(event_name);
        if not dates:
            dates = []
        dates.append([event[1], event[2]])
        events_dict[event_name]=dates

    event_length = len(events_dict)
    row_count = event_length // 2 + event_length % 2
    fig = make_subplots(
        rows=row_count, cols=2,
        subplot_titles=(list(events_dict.keys())))

    count = 1
    for key, value in events_dict.items():
        axes = []
        yes = []
        for val in value:
            axes.append(val[0])
            yes.append(val[1])
        row_number = count // 2 + count % 2
        col_number = 2 - count % 2
        fig.add_trace(go.Scatter(x=axes, y=yes, name=key), row=row_number, col=col_number)
        count += 1

    fig.update_layout(height=count*250, width=1500, title_text="Course event distribution per date")
    print("Opening browser...")
    fig.show()


def main(argv):
    print('Start events distribution calculation.')

    database_name = argv[1]
    user_name = argv[2]
    result_file = argv[3]

    connection = open_db_connection(database_name, user_name)
    events_distribution = calculate_events_distribution_per_day(connection)
    write_result_to_file(result_file, events_distribution)
    generate_figure(events_distribution)
    print('The analytics result can be found at ', result_file)
    close_db_connection(connection)


if __name__ == '__main__':
    main(sys.argv)
