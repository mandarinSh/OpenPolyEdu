import sys
import datetime
from database_services import *


def calculate_users(connection):
    print('Start query execution at ', datetime.datetime.now())

    get_unique_users_query = '''select DISTINCT log_line -> 'username' AS user from logs'''

    connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = connection.cursor()
    cursor.execute(get_unique_users_query)
    user_names = cursor.fetchall()
    cursor.close()
    connection.commit()

    print('End query execution at ', datetime.datetime.now())
    print("Users has been calculated")
    return user_names


def write_result_to_file(result_file, result):
    print('Start writing the data to file.')
    with open(result_file,"w") as file:
        for item in result:
            file.write("%s\n" % item)


def main(argv):
    print('Start calculating unique user names.')

    database_name = argv[1]
    user_name = argv[2]
    result_file = argv[3]

    connection = open_db_connection(database_name, user_name)
    user_names = calculate_users(connection)
    write_result_to_file(result_file, user_names)
    print('The analytics result can be found at ', result_file)
    close_db_connection(connection)


if __name__ == '__main__':
    main(sys.argv)
