import sys
import datetime
from database_services import *


def create_logs_table(connection):
    create_table_query = '''
        CREATE UNLOGGED TABLE logs
        (log_line jsonb NOT NULL)'''

    execute_query(connection, create_table_query)
    print("Table logs has been created")


def ingest_logs(connection, logs_file):
    print('Start ingesting logs at ', datetime.datetime.now())
    lines_in_batch = 100
    lines_array = []
    i = 0
    count = 0
    cur = connection.cursor()
    with open(logs_file, encoding="utf-8") as logs_file:
        for line in logs_file:
            if i < lines_in_batch:
                lines_array.append(line)
                i += 1
                count += 1
            else:
                records_list_template = ','.join(['(%s)'] * len(lines_array))
                insert_query = 'INSERT INTO logs(log_line) VALUES {}'.format(records_list_template)
                cur.execute(insert_query, lines_array)
                i = 0
                lines_array = []
                count += 1
                # Uncomment break for speedup test on limited number of records
                # break

    print('End ingesting logs at ', datetime.datetime.now())
    print('Records loaded: ', count)


def main(argv):
    print('Start loading logs to database.')

    database_name = argv[1]
    user_name = argv[2]
    openedu_log_file = argv[3]

    # The connection is used to create a new database for analytics
    connection = open_db_connection('postgres', user_name)
    create_database(connection, database_name)
    close_db_connection(connection)

    # The connection is used to create a table in analytics database
    connection = open_db_connection(database_name, user_name)
    create_logs_table(connection)
    ingest_logs(connection, openedu_log_file)
    close_db_connection(connection)


if __name__ == '__main__':
    main(sys.argv)
