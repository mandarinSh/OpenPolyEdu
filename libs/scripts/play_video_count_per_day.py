import sys
import datetime
import plotly.express as px
import pandas as pd
import csv
from database_services import *


def calculate_video_start_times(connection):
    print('Start query execution at ', datetime.datetime.now())

    get_play_video_times = '''select 
            TO_DATE(log_line ->> 'time', 'YYYY-MM-DD"T"HH24:MI:SS') as time_run, 
            count (*) as count_of_start
        from logs
        where log_line ->> 'event_type' = 'play_video'
        group by time_run
        order by time_run'''

    connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = connection.cursor()
    cursor.execute(get_play_video_times)
    video_start_times = cursor.fetchall()
    cursor.close()
    connection.commit()

    print('End query execution at ', datetime.datetime.now())
    print("Play video event times has been calculated")
    return video_start_times


def write_result_to_file(result_file, result):
    print('Start writing the data to file.')
    with open(result_file, mode='w') as res_file:
        field_names = ['time', 'count']
        result_file_writer = csv.writer(res_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        result_file_writer.writerow(field_names)
        for res in result:
            result_file_writer.writerow(res)


def generate_figure(file_with_data):
    df = pd.read_csv(file_with_data)
    fig = px.line(df, x='time', y='count')
    fig.show()


def main(argv):
    print('Start calculating play video times.')

    database_name = argv[1]
    user_name = argv[2]
    result_file = argv[3]

    connection = open_db_connection(database_name, user_name)
    video_start_times = calculate_video_start_times(connection)
    write_result_to_file(result_file, video_start_times)
    generate_figure(result_file)
    print('The analytics result can be found at ', result_file)
    close_db_connection(connection)


if __name__ == '__main__':
    main(sys.argv)
