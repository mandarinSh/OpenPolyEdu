import sys
import datetime
import plotly.express as px
import pandas as pd
import codecs
from tabulate import tabulate
from database_services import *


def unique_views_of_available_pdf(connection):
    print('Start query execution at ', datetime.datetime.now())

    user_pages_visited_at_timedate = """
        SELECT 
           count(*) AS count_number,
           trim((log_line ->> 'event')::json ->> 'query') as search_word
        FROM logs
        WHERE log_line ->> 'event_type' = 'textbook.pdf.search.executed'
        GROUP BY search_word
        ORDER BY count_number desc;
    """

    connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = connection.cursor()
    cursor.execute(user_pages_visited_at_timedate)
    user_way_on_course = cursor.fetchall()
    cursor.close()
    connection.commit()

    print('End query execution at ', datetime.datetime.now())
    print("Pdfs words has been calculated")
    return user_way_on_course


def write_result_to_file(result_file, result):
    print('Start writing the data to file.')
    with codecs.open(result_file,"w", "utf-8") as res_file:
        res_file.write(tabulate(result, headers=['count_number', 'word']))


def generate_figure(file_with_data):
    df = pd.read_csv(file_with_data)
    fig = px.bar(df, x='word', y='time')
    fig.show()


def main(argv):
    print('Start calculating words from pdfs.')

    database_name = argv[1]
    user_name = argv[2]
    result_file = argv[3]

    connection = open_db_connection(database_name, user_name)
    video_start_times = unique_views_of_available_pdf(connection)
    write_result_to_file(result_file, video_start_times)
    # generate_figure(result_file) no graph needed for this task
    print('The analytics result can be found at ', result_file)
    close_db_connection(connection)


if __name__ == '__main__':
    main(sys.argv)
