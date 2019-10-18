import sys
import datetime
import pandas as pd
from urllib.parse import unquote
import plotly.graph_objects as go
from database_services import *


def calculate_pages(connection):
    print('Start query execution at ', datetime.datetime.now())

    get_unique_pages_urls = '''select  
            log_line -> 'page' as section_name, 
            count(*) as interaction_count
        from logs
        where log_line ->> 'page' != 'null'
        group by section_name
        order by interaction_count desc'''

    connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = connection.cursor()
    cursor.execute(get_unique_pages_urls)
    pages_urls = cursor.fetchall()
    cursor.close()
    connection.commit()

    print('End query execution at ', datetime.datetime.now())
    return pages_urls


def process_urls(result):
    urls_without_parameters = dict()
    for item in result:
        url = item[0]

        if url.find('?') != -1:
            url = url[:url.find('?')]
        if url.find('#') != -1:
            url = url[:url.find('#')]

        url = unquote(url)

        if url.endswith('/'):
            url = url[:-1]

        interaction_count = urls_without_parameters.get(url)
        if not interaction_count:
            interaction_count = 0
        interaction_count += item[1]
        urls_without_parameters[url]=interaction_count

    return urls_without_parameters


def generate_figure(activity_distribution):
    print("Start figures generation...")

    axes = []
    yes = []
    for key, value in activity_distribution.items():
        axes.append(key)
        yes.append(value)

    fig = go.Figure(data=[go.Bar(
        x=axes, y=yes,
        text=yes,
        textposition='auto',
    )])

    fig.update_layout(title_text='Amount of interactions with the course pages',
                      autosize=False,
                      width=20*len(axes),
                      height=1000)
    print("Opening browser...")
    fig.show()


def write_result_to_file(result_file, result):
    print('Start writhing the data to file.')
    pd.DataFrame.from_dict(data=result, orient='index').to_csv(result_file, header=False)


def main(argv):
    print('Start calculating page activity on course (total number of visits).')

    database_name = argv[1]
    user_name = argv[2]
    result_file = argv[3]

    connection = open_db_connection(database_name, user_name)
    pages_urls = calculate_pages(connection)
    unique_urls_without_parameters = process_urls(pages_urls)
    write_result_to_file(result_file, unique_urls_without_parameters)
    generate_figure(unique_urls_without_parameters)
    print('The analytics result can be found at ', result_file)
    close_db_connection(connection)


if __name__ == '__main__':
    main(sys.argv)
