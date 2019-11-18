import sys
import datetime
from tabulate import tabulate
from database_services import *


def calculate_users_and_ids(connection):
    print('Start query execution at ', datetime.datetime.now())

    get_users_events_by_pages_query = '''select tbl.usr, tbl.evt, url_map.target_name, tbl.cnt from (
    with events (name) as (values ('play_video'), ('pause_video'), ('load_video'), ('edx.special_exam.proctored.attempt.started'), ('edx.ui.lms.outline.selected')),
    modules (url) as (	
	with pages (page) as (select distinct (log_line ->> 'page') from logs)
	select distinct
		case
    		when POSITION('?' in page) > 0 THEN SUBSTRING(page, 0, POSITION('?' in page))
    		when POSITION('#' in page) > 0 THEN SUBSTRING(page, 0, POSITION('#' in page))
    		else page
  		end as url
		from pages
		where page is not null
    ),
    mod_event (usr, mdl, evt) as (
	select
		coalesce (l.log_line ->> 'username', '<<' || (l.log_line #>> '{context, user_id}') || '>>'),
		case
    		when POSITION('?' in l.log_line ->> 'page') > 0 THEN SUBSTRING(l.log_line ->> 'page', 0, POSITION('?' in l.log_line ->> 'page'))
    		when POSITION('#' in l.log_line ->> 'page') > 0 THEN SUBSTRING(l.log_line ->> 'page', 0, POSITION('#' in l.log_line ->> 'page'))
    		else l.log_line ->> 'page'
  		end as url,
		l.log_line ->> 'event_type'
	from logs as l
    )
    select usr, mdl, evt, count(*) as cnt from mod_event
    where mdl in (select url from modules)
    	and evt in (select name from events)
    group by usr, mdl, evt
	) tbl	
	join (
		select 
				url_decode((log_line ->> 'event')::json ->> 'target_url') as target_url,
				(log_line ->> 'event')::json ->> 'target_name' as target_name
            from logs 
            where 
				(log_line ->> 'event_type' LIKE '%link_clicked' or 
				log_line ->> 'event_type' LIKE '%selected')
				and (log_line ->> 'event')::json ->> 'target_name' is not null
				and (log_line ->> 'event')::json ->> 'target_name' not LIKE '%текущий раздел%'
            GROUP BY target_name, target_url	
	) url_map
	on tbl.mdl = url_map.target_url	
    order by usr'''

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
    with open(result_file,"w", encoding="utf-8") as file:
        file.write(tabulate(result, headers=['user_name', 'event_type', 'page', 'count_events']))


def generate_figure(user_names):
    pass


def main(argv):
    print('Start calculating unique user names.')

    database_name = argv[1]
    user_name = argv[2]
    result_file = argv[3]

    connection = open_db_connection(database_name, user_name)
    # get_all_pages_names(connection)
    users_events_by_pages = calculate_users_and_ids(connection)
    write_result_to_file(result_file, users_events_by_pages)
    print('The analytics result can be found at ', result_file)
    close_db_connection(connection)


if __name__ == '__main__':
    main(sys.argv)
