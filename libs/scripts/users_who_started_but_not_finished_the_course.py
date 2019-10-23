import sys
import datetime
from tabulate import tabulate
from database_services import *


def calculate_users_who_enrolled_but_not_started(connection):
    print('Start query execution at ', datetime.datetime.now())

    get_users_who_not_finished_the_course_query = '''
        select allUsers.user_id as user_id, allUsers.user_name as user_name from (
            select uniqueUserIds.user_id as user_id, userAndIDs.user_name as user_name from (
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
        ) allUsers
        INNER JOIN (		
			select userTimeOnCourse.user_id as user_id from (
				select total_time_per_day.user_id as user_id, SUM(total_time_per_day.time_at_session_per_day) as duration from (
					select durationTable.session_user_id as user_id, durationTable.session_date, SUM(durationTable.session_duration) as time_at_session_per_day from (
							select
								log_line #>> '{context, user_id}' as session_user_id,
								TO_DATE(log_line ->> 'time', 'YYYY-MM-DD"T"HH24:MI:SS')::DATE as session_date,
								log_line -> 'session' as session_name,
								age(MAX(TO_TIMESTAMP(log_line ->> 'time', 'YYYY-MM-DD"T"HH24:MI:SS')::TIMESTAMP), MIN(TO_TIMESTAMP(log_line ->> 'time', 'YYYY-MM-DD"T"HH24:MI:SS')::TIMESTAMP)) as session_duration
							from logs
							where log_line ->> 'session' != 'null' and log_line ->> 'session' != ''
								group by session_user_id, session_name, session_date
						) durationTable
						group by durationTable.session_user_id, durationTable.session_date
				) total_time_per_day
				group by total_time_per_day.user_id
			) userTimeOnCourse
			LEFT JOIN (
				select 
					log_line #>> '{context, user_id}' as user_id
				from logs where log_line ->> 'name' LIKE 'edx.special_exam%'
				group by user_id
			) usersWhoStartedAnyExam
			ON userTimeOnCourse.user_id = usersWhoStartedAnyExam.user_id
			where usersWhoStartedAnyExam.user_id is null and userTimeOnCourse.duration > '00:00:00'
         ) usersWhoStartedCourseAndDidntTryAnyExam
        ON allUsers.user_id = usersWhoStartedCourseAndDidntTryAnyExam.user_id
        group by allUsers.user_id, user_name
        order by user_name desc NULLS last'''

    connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = connection.cursor()
    cursor.execute(get_users_who_not_finished_the_course_query)
    started_but_not_finished_users = cursor.fetchall()
    cursor.close()
    connection.commit()

    print('End query execution at ', datetime.datetime.now())
    print("Users who started teh course, but not finished it are calculated")
    return started_but_not_finished_users


def write_result_to_file(result_file, result):
    print('Start writing the data to file.')
    with open(result_file,"w") as file:
        file.write(tabulate(result, headers=['user_id', 'user_name']))


def main(argv):
    print('Start calculating user who started the course, but not finished it.')
    print('It means that user performed any action in course,'
          'but have not even started the final exam.')

    database_name = argv[1]
    user_name = argv[2]
    result_file = argv[3]

    connection = open_db_connection(database_name, user_name)
    started_but_not_finished_users = calculate_users_who_enrolled_but_not_started(connection)
    write_result_to_file(result_file, started_but_not_finished_users)
    print('The analytics result can be found at ', result_file)
    close_db_connection(connection)


if __name__ == '__main__':
    main(sys.argv)
