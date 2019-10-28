import sys
import datetime
from tabulate import tabulate
from database_services import *


def calculate_users_and_ids(connection):
    print('Start query execution at ', datetime.datetime.now())

    # This query can be used to get usernames, ids, their counts of events,
    # sessions, pages visited (but not sure it is correct)
    get_unique_users_query = '''select 
				log_line -> 'username' as user_name,
				log_line #>> '{context, user_id}' AS user_id,
				count (*) as e_count,
				count (distinct log_line -> 'session') as sessions_count,
				count (distinct log_line -> 'page') as pages_count
				
			from logs
			where log_line -> 'event' != '""' 
				and log_line -> 'username' != 'null' 
				and log_line -> 'username' != '""' 
				and log_line -> 'username' is not null
				and log_line -> 'page' != 'null'
				
			group by user_id, user_name
		order by user_name;'''

    # This query is used to get all users and count of each event for every user
    get_unique_events_by_users_query = '''WITH user_events(user_name, user_id, event_type) AS (
	    SELECT log_line ->> 'username', log_line #>> '{context, user_id}', log_line ->> 'event_type'
	    FROM logs
	    WHERE log_line #>> '{context, user_id}' IS NOT NULL
    ),
    groupped(user_name_or_id, event_type, cnt) AS (
	    SELECT COALESCE(NULLIF(user_name, ''), '<<' || user_id || '>>'), event_type, COUNT(*)
	    FROM user_events
	    GROUP BY user_name, user_id, event_type
    )
    SELECT * FROM groupped
    ORDER BY user_name_or_id, event_type;''';

    connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = connection.cursor()
    cursor.execute(get_unique_events_by_users_query)
    user_names = cursor.fetchall()
    cursor.close()
    connection.commit()

    print('End query execution at ', datetime.datetime.now())
    print("Users and ids has been calculated")
    return user_names


def write_result_to_file(result_file, result):
    print('Start writing the data to file.')
    with open(result_file,"w") as file:
        file.write(tabulate(result, headers=['user_name', 'event_type', 'count_events']))


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
