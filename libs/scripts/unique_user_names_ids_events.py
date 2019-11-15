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
    for name in page_names:
        print(name[0], '\n')
    return page_names


def calculate_users_and_ids(connection):
    print('Start query execution at ', datetime.datetime.now())

    page_names = get_all_pages_names(connection)

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

    get_users_events_by_pages_query = '''with events (name) as 
    (values ('play_video'), ('load_video'), ('edx.special_exam.proctored.attempt.started'), ('edx.ui.lms.outline.selected')),
    modules (url) as (		
	with pages (page) as (select distinct (log_line ->> 'page') from logs)
	select distinct url from (
		select page,
		case
    		when POSITION('?' in page) > 0 THEN SUBSTRING(page, 0, POSITION('?' in page))
    		when POSITION('#' in page) > 0 THEN SUBSTRING(page, 0, POSITION('#' in page))
    		else page
  		end as url
		from pages
		where page is not null) 
	as urls
    ),
    mod_event (usr, pg, mdl, evt) as (
	with pages (page) as (select distinct (log_line ->> 'page') from logs)
	select
		coalesce (l.log_line ->> 'username', '<<' || (l.log_line #>> '{context, user_id}') || '>>'),
		pg.page,
		case
    		when POSITION('?' in pg.page) > 0 THEN SUBSTRING(pg.page, 0, POSITION('?' in pg.page))
    		when POSITION('#' in pg.page) > 0 THEN SUBSTRING(pg.page, 0, POSITION('#' in pg.page))
    		else pg.page
  		end as url,	
		l.log_line ->> 'event_type'
	from logs as l, pages as pg
    )
    select usr, mdl, evt, count (*) from mod_event
    where mdl in (select url from modules)
	    and evt in (select name from events)
    group by usr, mdl, evt'''

    connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = connection.cursor()
    cursor.execute(get_users_events_by_pages_query)
    users_events_by_pages = cursor.fetchall()
    cursor.close()
    connection.commit()

    print('End query execution at ', datetime.datetime.now())
    print("Users and ids has been calculated")
    return users_events_by_pages


def write_result_to_file(result_file, result):
    print('Start writing the data to file.')
    with open(result_file,"w") as file:
        file.write(tabulate(result, headers=['user_name', 'module', 'event_type', 'count_events']))


def generate_figure(user_names):
    pass


def main(argv):
    print('Start calculating unique user names.')

    database_name = argv[1]
    user_name = argv[2]
    result_file = argv[3]

    connection = open_db_connection(database_name, user_name)
    get_all_pages_names(connection)
    users_events_by_pages = calculate_users_and_ids(connection)
    write_result_to_file(result_file, users_events_by_pages)
    print('The analytics result can be found at ', result_file)
    close_db_connection(connection)


if __name__ == '__main__':
    main(sys.argv)
