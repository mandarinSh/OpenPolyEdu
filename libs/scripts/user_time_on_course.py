import sys
import datetime
from tabulate import tabulate
import plotly.graph_objects as go
from database_services import *


def calculate_user_time_on_course(connection):
    print('Start query execution at ', datetime.datetime.now())

    user_time_on_course_query = '''select durationTable.session_user_id, SUM(durationTable.session_duration) as time_at_course from (
            select
                log_line #>> '{context, user_id}' as session_user_id,
                log_line -> 'session' as session_name,
                age(MAX(TO_TIMESTAMP(log_line ->> 'time', 'YYYY-MM-DD"T"HH24:MI:SS')::TIMESTAMP), MIN(TO_TIMESTAMP(log_line ->> 'time', 'YYYY-MM-DD"T"HH24:MI:SS')::TIMESTAMP)) as session_duration
            from logs
            where log_line ->> 'session' != 'null' and log_line ->> 'session' != ''
            group by session_user_id, session_name
        ) durationTable
        group by durationTable.session_user_id
        order by time_at_course desc'''

    connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = connection.cursor()
    cursor.execute(user_time_on_course_query)
    user_time_on_course = cursor.fetchall()
    cursor.close()
    connection.commit()

    print('End query execution at ', datetime.datetime.now())
    return user_time_on_course


def generate_figure(user_time_on_course):
    print("Start figures generation...")

    index = 1
    x_axis = []
    y_axis = []

    for duration in user_time_on_course:
        x_axis.append(index)
        y_axis.append(duration[1].total_seconds()/ (60 * 60))
        index += 1

    fig = go.Figure(data=go.Scatter(x=x_axis, y=y_axis))

    fig.update_layout(
        height=500,
        width=2000,
        title_text="User time on course.",
        xaxis=go.layout.XAxis(
            title=go.layout.xaxis.Title(
                text="User order number",
                font=dict(
                    family="Courier New, monospace",
                    size=18,
                    color="#7f7f7f"
                )
            )
        ),
        yaxis=go.layout.YAxis(
            title=go.layout.yaxis.Title(
                text="Time in hours",
                font=dict(
                    family="Courier New, monospace",
                    size=18,
                    color="#7f7f7f"
                )
            )
        ))

    print("Opening browser...")
    fig.show()


def write_result_to_file(result_file, result):
    print('Start writing the data to file.')
    with open(result_file,"w") as file:
        file.write(tabulate(result, headers=['user_name', 'time_on_course']))


def main(argv):
    print('Start calculating user time on course.')

    database_name = argv[1]
    user_name = argv[2]
    result_file = argv[3]

    connection = open_db_connection(database_name, user_name)
    user_time_on_course = calculate_user_time_on_course(connection)
    write_result_to_file(result_file, user_time_on_course)
    generate_figure(user_time_on_course)
    print('The analytics result can be found at ', result_file)
    close_db_connection(connection)


if __name__ == '__main__':
    main(sys.argv)
