import sys
import datetime
import csv
import ntpath
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from database_services import *


def calculate_events_distribution_per_day(connection, user_id):
    print('Start query execution at ', datetime.datetime.now())

    get_distribution_events = '''select 
            log_line ->> 'name' as event_name,
            TO_DATE(log_line ->> 'time', 'YYYY-MM-DD"T"HH24:MI:SS') as time_run,
            count (*) as count_of_start
        from logs
        where log_line ->> 'name' != \'\''''

    if user_id:
        get_distribution_events += ''' and log_line #>> '{context, user_id}' = \'''' + user_id + '\''

    get_distribution_events += ''' group by time_run, event_name
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


def write_result_to_file(result_file, result, user_id):
    print("Writing results to file")
    if user_id:
        path = ntpath.dirname(result_file)
        filename = user_id + '_user_type_activity_on_course.csv'
        result_file = path + "/" + filename
    with open(result_file, mode='w') as res_file:
        field_names = ['time', 'event_name', 'count']
        result_file_writer = csv.writer(res_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        result_file_writer.writerow(field_names)
        for res in result:
            result_file_writer.writerow(res)


def generate_figure(event_distribution, user_id):
    print("Start figures generation...")
    events_dict = dict()
    for event in event_distribution:
        event_name = event[0]
        dates = events_dict.get(event_name)
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
        x_axis = []
        y_axis = []
        for val in value:
            x_axis.append(val[0])
            y_axis.append(val[1])
        row_number = count // 2 + count % 2
        col_number = 2 - count % 2
        fig.add_trace(go.Scatter(x=x_axis, y=y_axis, name=key), row=row_number, col=col_number)
        count += 1

    title = "Course activity types, that usees performed, depending on date"
    if user_id:
        title = "User '" + user_id + "' activity types on course depending on day"

    fig.update_layout(height=count*250, width=1500, title_text=title)
    print("Opening browser...")
    fig.show()


def main(argv):
    print('Type user id to analyze his/her activity types. '
          'If no user id is provided, then total activity on '
          'course for every activity type is calculated.')
    user_id = input("User id: ")

    print('Start events distribution calculation.')

    database_name = argv[1]
    user_name = argv[2]
    result_file = argv[3]

    connection = open_db_connection(database_name, user_name)
    events_distribution = calculate_events_distribution_per_day(connection, user_id)
    write_result_to_file(result_file, events_distribution, user_id)
    generate_figure(events_distribution, user_id)
    print('The analytics result can be found at ', result_file)
    close_db_connection(connection)


if __name__ == '__main__':
    main(sys.argv)
