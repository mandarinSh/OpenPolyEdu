import sys
import datetime
import re
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


def calculate_urls_and_names_mapping(connection):
    print('Start query execution at ', datetime.datetime.now())

    get_urls_and_names_mapping_query = '''select uniqueUrls.target_url as target_url, urlsAndIDs.target_name as target_name from (
            select 
                url_decode((log_line ->> 'event')::json ->> 'target_url') as target_url
            from logs
			where 
				log_line ->> 'event_type' LIKE '%link_clicked' or 
				log_line ->> 'event_type' LIKE '%selected'
            GROUP BY target_url 
        ) uniqueUrls
        LEFT JOIN (
            select 
				url_decode((log_line ->> 'event')::json ->> 'target_url') as target_url,
				(log_line ->> 'event')::json ->> 'target_name' as target_name
            from logs 
            where 
				(log_line ->> 'event_type' LIKE '%link_clicked' or 
				log_line ->> 'event_type' LIKE '%selected')
				and (log_line ->> 'event')::json ->> 'target_name' is not null
            GROUP BY target_name, target_url
        ) urlsAndIDs
        ON uniqueUrls.target_url = urlsAndIDs.target_url
		where uniqueUrls.target_url is not null
        order by target_name'''

    connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = connection.cursor()
    cursor.execute(get_urls_and_names_mapping_query)
    urls_and_names_mapping = cursor.fetchall()
    cursor.close()
    connection.commit()

    print('End query execution at ', datetime.datetime.now())
    print("Urls and names mapping has been calculated")
    return urls_and_names_mapping


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

        m = re.search(r'/\d$', url)
        if m is not None:
            url = url[:-2]

        interaction_count = urls_without_parameters.get(url)
        if not interaction_count:
            interaction_count = 0
        interaction_count += item[1]
        urls_without_parameters[url]=interaction_count

    return urls_without_parameters


def find_alias(url, urls_and_names_mapping):
    for url_mapping in urls_and_names_mapping:
        if url_mapping[0] == url + '/':
            return url_mapping[1]
    return None


def generate_figure(activity_distribution, urls_and_names_mapping):
    print("Start figures generation...")

    x_axis = []
    y_axis = []
    for key, value in activity_distribution.items():
        alias = find_alias(key, urls_and_names_mapping)
        if alias:
            x_axis.append(alias + " (" + key + ")")
        else:
            x_axis.append(key)
        y_axis.append(value)

    fig = go.Figure(data=[go.Bar(
        x=y_axis, y=x_axis,
        text=y_axis,
        textposition='auto',
        orientation='h'
    )])

    fig.update_layout(title_text='Amount of interactions with the course pages',
                      autosize=False,
                      width=5000,
                      height=30*len(x_axis))
    print("Opening browser...")
    fig.show()


def write_result_to_file(result_file, result):
    print('Start writing the data to file.')
    pd.DataFrame.from_dict(data=result, orient='index').to_csv(result_file, header=False)


def main(argv):
    print('Start calculating page activity on course (total number of visits).')

    database_name = argv[1]
    user_name = argv[2]
    result_file = argv[3]

    connection = open_db_connection(database_name, user_name)
    pages_urls = calculate_pages(connection)
    unique_urls_without_parameters = process_urls(pages_urls)
    urls_and_names_mapping = calculate_urls_and_names_mapping(connection)
    write_result_to_file(result_file, unique_urls_without_parameters)
    generate_figure(unique_urls_without_parameters, urls_and_names_mapping)
    print('The analytics result can be found at ', result_file)
    close_db_connection(connection)


if __name__ == '__main__':
    main(sys.argv)
