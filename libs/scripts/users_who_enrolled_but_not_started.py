import sys
import datetime
from tabulate import tabulate
from database_services import *


def calculate_users_who_enrolled_but_not_started(connection):
    print('Start query execution at ', datetime.datetime.now())

    get_enrolled_but_not_started_users_query = '''select notStartedUsers.enrolled_but_not_started as user_id, userNames.user_name as user_name from (
            select enrolledUsers.user_id as enrolled_but_not_started from (
                select   
                    log_line #>> '{event, user_id}' as user_id
                from logs
                where log_line #>> '{event_type}' = 'edx.course.enrollment.activated'		
            ) enrolledUsers
            LEFT JOIN (
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
            ON userTimeOnCourse.user_id = enrolledUsers.user_id
            where userTimeOnCourse.user_id is null or duration = '00:00:00'
        ) notStartedUsers
        INNER JOIN (
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
        ) userNames
        ON userNames.user_id = notStartedUsers.enrolled_but_not_started
        group by user_name, notStartedUsers.enrolled_but_not_started        
        order by user_name desc NULLS LAST'''

    connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = connection.cursor()
    cursor.execute(get_enrolled_but_not_started_users_query)
    enrolled_but_not_started_users = cursor.fetchall()
    cursor.close()
    connection.commit()

    print('End query execution at ', datetime.datetime.now())
    print("Enrolled but not started users are calculated")
    return enrolled_but_not_started_users


def write_result_to_file(result_file, result):
    print('Start writing the data to file.')
    with open(result_file,"w") as file:
        file.write(tabulate(result, headers=['user_id', 'user_name']))


def main(argv):
    print('Start calculating user who enrolled, but not started course.')
    print('It means that there is enrolment event has '
          'generated and the total time on course is \'0\'.')

    database_name = argv[1]
    user_name = argv[2]
    result_file = argv[3]

    connection = open_db_connection(database_name, user_name)
    enrolled_but_not_started_users = calculate_users_who_enrolled_but_not_started(connection)
    write_result_to_file(result_file, enrolled_but_not_started_users)
    print('The analytics result can be found at ', result_file)
    close_db_connection(connection)


if __name__ == '__main__':
    main(sys.argv)
