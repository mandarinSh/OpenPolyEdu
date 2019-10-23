import sys
import datetime
import codecs
from tabulate import tabulate
from database_services import *


def calculate_urls_and_names_mapping(connection):
    print('Start query execution at ', datetime.datetime.now())

    get_urls_and_names_mapping_query = '''select
            url_decode((log_line ->> 'event')::json ->> 'target_url') as target_url,
            (log_line ->> 'event')::json ->> 'target_name' as target_name		
        from logs
        where 
            (log_line ->> 'event_type' LIKE '%link_clicked' or 
            log_line ->> 'event_type' LIKE '%selected' or 
            log_line ->> 'event_type' LIKE '%next_selected' or 
            log_line ->> 'event_type' LIKE '%next_selected' or 
            log_line ->> 'event_type' LIKE '%previous_selected' or 
            log_line ->> 'event_type' LIKE '%tab_selected')
        group by target_url, target_name
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


def write_result_to_file(result_file, result):
    print('Start writing the data to file.')
    with codecs.open(result_file,"w", "utf-8") as file:
        file.write(tabulate(result, headers=['target_url', 'target_name']))


def main(argv):
    print('Start calculating urls and names mapping.')

    database_name = argv[1]
    user_name = argv[2]
    result_file = argv[3]

    connection = open_db_connection(database_name, user_name)
    urls_and_names = calculate_urls_and_names_mapping(connection)
    write_result_to_file(result_file, urls_and_names)
    print('The analytics result can be found at ', result_file)
    close_db_connection(connection)


if __name__ == '__main__':
    main(sys.argv)
