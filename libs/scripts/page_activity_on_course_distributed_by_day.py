import sys
import datetime
import pandas as pd
from urllib.parse import unquote
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from database_services import *


def calculate_page_activity_per_day(connection):
    print('Start query execution at ', datetime.datetime.now())

    page_activity_per_day_query = '''select   
            log_line -> 'page' as section_name, 
            TO_DATE(log_line ->> 'time', 'YYYY-MM-DD"T"HH24:MI:SS') as time_run,
            count(*) as interaction_count
        from logs
        where log_line ->> 'page' != 'null'
        group by section_name, time_run
        order by interaction_count desc'''

    connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = connection.cursor()
    cursor.execute(page_activity_per_day_query)
    page_activity_per_day = cursor.fetchall()
    cursor.close()
    connection.commit()

    print('End query execution at ', datetime.datetime.now())
    return page_activity_per_day


def process_urls(result):
    page_activity_per_day_clean = dict()
    for item in result:
        url = item[0]

        if url.find('?') != -1:
            url = url[:url.find('?')]
        if url.find('#') != -1:
            url = url[:url.find('#')]

        url = unquote(url)

        if url.endswith('/'):
            url = url[:-1]

        dates = page_activity_per_day_clean.get(url)
        if not dates:
            dates = dict()

        interaction_count = dates.get(item[1])
        if not interaction_count:
            interaction_count = 0

        interaction_count += item[2]
        dates[item[1]] = interaction_count

        page_activity_per_day_clean[url]=dates

    return page_activity_per_day_clean


def generate_figure(page_activity_per_day):
    print("Start figures generation...")

    pages_length = len(page_activity_per_day)
    row_count = pages_length
    fig = make_subplots(
        rows=row_count,
        cols=1,
        subplot_titles=(list(page_activity_per_day.keys())))

    count = 1
    for key, value in page_activity_per_day.items():
        x_axis = []
        y_axis = []
        for date in sorted(value.keys()):
            x_axis.append(date)
            y_axis.append(value.get(date))
        row_number = count
        col_number = 1
        fig.add_trace(go.Scatter(x=x_axis, y=y_axis, name=key), row=row_number, col=col_number)
        count += 1

    fig.update_layout(
        height=count*250,
        width=2500,
        title_text="Page activity on course distributed by day.")
    print("Opening browser...")
    fig.show()


def write_result_to_file(result_file, result):
    print('Start writing the data to file.')
    pd.DataFrame.from_dict(data=result, orient='index').to_csv(result_file, header=False)


def main(argv):
    print('Start calculating page activity on course distributed by day.')

    database_name = argv[1]
    user_name = argv[2]
    result_file = argv[3]

    connection = open_db_connection(database_name, user_name)
    page_activity_per_day = calculate_page_activity_per_day(connection)
    clean_page_activity_per_day = process_urls(page_activity_per_day)
    write_result_to_file(result_file, clean_page_activity_per_day)
    generate_figure(clean_page_activity_per_day)
    print('The analytics result can be found at ', result_file)
    close_db_connection(connection)


if __name__ == '__main__':
    main(sys.argv)
