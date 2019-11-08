import sys
import datetime
from tabulate import tabulate
from database_services import *


def get_all_pages_names(connection):
    print('Start query execution at ', datetime.datetime.now())

    all_pages_query = '''select target_names.target_name from 
    	(
    		select url_decode((log_line ->> 'event')::json ->> 'target_name') as target_name 
    		from logs
    		where 
    			(log_line ->> 'event_type' LIKE '%link_clicked' or 
    				log_line ->> 'event_type' LIKE '%selected')
    				and (log_line ->> 'event')::json ->> 'target_name' is not null
    		group by target_name
    	) target_names;'''

    connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = connection.cursor()
    cursor.execute(all_pages_query)
    page_names = cursor.fetchall()
    cursor.close()
    connection.commit()

    print('End query execution at ', datetime.datetime.now())
    print("Users and ids has been calculated")
    return page_names


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

    third_query = '''select 
	user_events.user_name as user_name, 
	user_events.user_id as user_id,
	user_events.e_count as total_events_count,
	user_events.sessions_count as sessions_count,
	user_events.pages_count as pages_count,
	count_plays.play_count as play_count,
 	exam_started_event.exam_started as exam_started,	
 	speed_change_video_events.speed_change_video as speed_change_video
	from (
		select
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
		) user_events
			
			left join (
				select 
					log_line -> 'username' as user_name,
					log_line #>> '{context, user_id}' AS user_id,
					count (log_line -> 'event_type') as play_count
				from logs
				where log_line ->> 'event_type' = 'play_video'
				group by user_id, user_name
			) count_plays
			on user_events.user_id = count_plays.user_id
						
 			left join (
 				select 
 					log_line -> 'username' as user_name,
 					log_line #>> '{context, user_id}' AS user_id,
 					count (log_line -> 'event_type') as exam_started
 				from logs
 				where (log_line ->> 'event_type' =  'edx.special_exam.timed.attempt.started')
 				group by user_id, user_name
 			) exam_started_event
 			on user_events.user_id = exam_started_event.user_id
			
			left join (
 				select 
 					log_line -> 'username' as user_name,
 					log_line #>> '{context, user_id}' AS user_id,
 					count (log_line -> 'event_type') as speed_change_video
 				from logs
 				where log_line ->> 'event_type' = 'speed_change_video'
 				group by user_id, user_name
 			) speed_change_video_events
 			on user_events.user_id = speed_change_video_events.user_id
		
		order by user_name;'''



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


def generate_figure(user_names):
    pass


def main(argv):
    print('Start calculating unique user names.')

    database_name = argv[1]
    user_name = argv[2]
    result_file = argv[3]

    connection = open_db_connection(database_name, user_name)
    get_all_pages_names(connection)
    # user_names_and_ids = calculate_users_and_ids(connection)
    # write_result_to_file(result_file, user_names_and_ids)
    # print('The analytics result can be found at ', result_file)
    close_db_connection(connection)


if __name__ == '__main__':
    main(sys.argv)
