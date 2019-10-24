import sys
import re
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


def write_result_to_file(result_file, result, urls_and_names_mapping):
    print('Start writing the data to file.')
    with open(result_file, mode='w', encoding="utf-8") as res_file:
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

    m = re.search(r'/\d$', url)
    if m is not None:
        url = url[:-2]

    return url


def find_alias(url, urls_and_names_mapping):
    for url_mapping in urls_and_names_mapping:
        if url_mapping[0] == url + '/':
            return url_mapping[1]
    return None


def generate_figure(user_way_on_course, urls_and_names_mapping, user_id):
    x_axis = []
    y_axis = []

    y_ticktext = []
    for user in user_way_on_course:
        if user[0]:
            x_axis.append(user[0])
            cleaned_url = process_urls(user[1])
            y_axis.append(cleaned_url)

            alias = find_alias(cleaned_url, urls_and_names_mapping)
            if alias:
                y_ticktext.append(alias)
            else:
                y_ticktext.append(cleaned_url)

    fig = go.Figure(data=go.Scatter(x=x_axis, y=y_axis, line=dict(width=5, color='#b22222'),
                                    mode='lines+markers',
                                    marker_size=15))

    fig.update_layout(
        height=1000,
        width=10000,
        title_text="Way of moving on course per day of the user with id '" + str(user_id) + "'",
        xaxis=go.layout.XAxis(
            title=go.layout.xaxis.Title(
                text="Date of moving",
                font=dict(
                    family="Courier New, monospace",
                    size=18,
                    color="#7f7f7f"
                )
            ),
            tickmode='array'
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

    fig.update_yaxes(
        ticktext=y_ticktext,
        tickvals=y_axis
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
    urls_and_names_mapping = calculate_urls_and_names_mapping(connection)
    write_result_to_file(result_file, user_way_on_course, urls_and_names_mapping)
    generate_figure(user_way_on_course, urls_and_names_mapping, user_id)
    print('The analytics result can be found at ', result_file)
    close_db_connection(connection)


if __name__ == '__main__':
    main(sys.argv)
