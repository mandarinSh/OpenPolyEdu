import sys
import datetime
from tabulate import tabulate
from database_services import *


def calculate_users_and_ids(connection):
    print('Start query execution at ', datetime.datetime.now())

    # It is required to obtain list of unique ids first and then join it with names, because
    # it is possible, that EDX does not generate 'name' for some events
    get_unique_users_query = '''select userAndIDs.user_name as user_name, uniqueUserIds.user_id as user_id from (
            select 
                log_line #>> '{context, user_id}' AS user_id 
            from logs 
            GROUP BY user_id 
        ) uniqueUserIds
        LEFT JOIN (
            select 
                log_line -> 'username' as user_name,
                log_line #>> '{context, user_id}' AS user_id 
            from logs 
            where log_line -> 'username' != 'null' and log_line -> 'username' != '""' and log_line -> 'username' is not null
            GROUP BY user_id, user_name
        ) userAndIDs
        ON uniqueUserIds.user_id = userAndIDs.user_id
        order by user_name'''

    connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = connection.cursor()
    cursor.execute(get_unique_users_query)
    user_names = cursor.fetchall()
    cursor.close()
    connection.commit()

    print('End query execution at ', datetime.datetime.now())
    print("Users and ids has been calculated")
    return user_names


def write_result_to_file(result_file, result):
    print('Start writing the data to file.')
    with open(result_file,"w") as file:
        file.write(tabulate(result, headers=['user_name', 'user_id']))


def main(argv):
    print('Start calculating unique user names.')

    database_name = argv[1]
    user_name = argv[2]
    result_file = argv[3]

    connection = open_db_connection(database_name, user_name)
    user_names_and_ids = calculate_users_and_ids(connection)
    write_result_to_file(result_file, user_names_and_ids)
    print('The analytics result can be found at ', result_file)
    close_db_connection(connection)


if __name__ == '__main__':
    main(sys.argv)
