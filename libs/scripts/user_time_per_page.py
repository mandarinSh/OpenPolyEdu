import sys
import datetime
from tabulate import tabulate
from database_services import *


def calculate_users_video_duration(connection):
    print('Start query execution at ', datetime.datetime.now())

    # TODO
    print('End query execution at ', datetime.datetime.now())
    print("Users time per page has been calculated")
    print("")
    return []


def write_result_to_file(result_file, result):
    file = open(result_file,"w")
    file.write(tabulate(result, headers=['user_name', 'user_id']))
    file.close()


def main(argv):
    print('Start calculating user\'s times per page.')

    database_name = argv[1]
    user_name = argv[2]
    result_file = argv[3]

    connection = open_db_connection(database_name, user_name)
    user_names_and_ids = calculate_users_video_duration(connection)
    write_result_to_file(result_file, user_names_and_ids)
    print('The analytics result can be found at ', result_file)
    close_db_connection(connection)


if __name__ == '__main__':
    main(sys.argv)
