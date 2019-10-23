import sys
import datetime
from urllib.parse import unquote
import plotly.graph_objects as go
import csv
from database_services import *


def calculate_user_way_of_moving(connection, user_id):
    print('Start query execution at ', datetime.datetime.now())

    user_pages_visited_at_timedate = '''select 
            TO_TIMESTAMP(log_line ->> 'time', 'YYYY-MM-DD"T"HH24:MI:SS')::TIMESTAMP as time_access,
            log_line ->>'page' as page_visited
        from logs
        where 
        log_line #>> '{context, user_id}' = \'''' + user_id + '''\'
        and log_line ->>'page' is not null 
            and log_line ->>'page' != 'x_module'
            order by time_access'''

    connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = connection.cursor()
    cursor.execute(user_pages_visited_at_timedate)
    user_way_on_course = cursor.fetchall()
    cursor.close()
    connection.commit()

    print('End query execution at ', datetime.datetime.now())
    print("User way has been calculated")
    return user_way_on_course


def write_result_to_file(result_file, result):
    print('Start writing the data to file.')
    with open(result_file, mode='w') as res_file:
        field_names = ['time_access', 'page_url']
        result_file_writer = csv.writer(res_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        result_file_writer.writerow(field_names)
        for res in result:
            result_file_writer.writerow(res)


def process_urls(url):
    if url.find('?') != -1:
        url = url[:url.find('?')]
    if url.find('#') != -1:
        url = url[:url.find('#')]

    url = unquote(url)

    if url.endswith('/'):
        url = url[:-1]

    return url


def generate_figure(user_way_on_course, user_id):
    x_axis = []
    y_axis = []
    for user in user_way_on_course:
        if user[0]:
            x_axis.append(user[0])
            y_axis.append(process_urls(user[1]))

    fig = go.Figure(data=go.Scatter(x=x_axis, y=y_axis, line=dict(width=5, color='#b22222'),
                                    mode='lines+markers',
                                    marker_size=15))

    fig.update_layout(
        height=1000,
        width=20000,
        title_text="Way of moving on course per day of the user with id '" + str(user_id) + "'",
        xaxis=go.layout.XAxis(
            title=go.layout.xaxis.Title(
                text="Date of moving",
                font=dict(
                    family="Courier New, monospace",
                    size=18,
                    color="#7f7f7f"
                )
            )
        ),
        yaxis=go.layout.YAxis(
            title=go.layout.yaxis.Title(
                text="Page URL",
                font=dict(
                    family="Courier New, monospace",
                    size=18,
                    color="#7f7f7f"
                )
            )
        )
    )

    print("Opening browser...")
    fig.show()


def main(argv):
    print('Type user id to analyze his/her way of moving over teh course page URLs. '
          'User id is mandatory for the analysis.')
    user_id = input("User id: ")

    if not user_id:
        print('No analysis is performed. \'User id\' is required.')
        return

    print('Start calculating user way.')

    database_name = argv[1]
    user_name = argv[2]
    result_file = argv[3]

    connection = open_db_connection(database_name, user_name)
    user_way_on_course = calculate_user_way_of_moving(connection, user_id)
    write_result_to_file(result_file, user_way_on_course)
    generate_figure(user_way_on_course, user_id)
    print('The analytics result can be found at ', result_file)
    close_db_connection(connection)


if __name__ == '__main__':
    main(sys.argv)
