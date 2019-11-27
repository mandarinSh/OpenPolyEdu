import sys
import datetime
from tabulate import tabulate
from database_services import *
import csv
import xlsxwriter


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
    				and (log_line ->> 'event')::json ->> 'target_name' not LIKE '%текущий раздел%'
    		group by target_name
    	) target_names;'''

    connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = connection.cursor()
    cursor.execute(all_pages_query)
    page_names = cursor.fetchall()
    cursor.close()
    connection.commit()

    print("Pages and page names has been calculated")
    # print(page_names)
    return page_names


def get_all_users(connection):
    print('Start query execution at ', datetime.datetime.now())

    all_users_query = '''select distinct log_line ->> 'username' as username from logs order by username;'''

    connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = connection.cursor()
    cursor.execute(all_users_query)
    user_names = cursor.fetchall()
    cursor.close()
    connection.commit()

    print("Users has been calculated")
    # print(user_names)

    return user_names


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


def write_result_to_table_file(result_file, result, page_names, user_names):
    print('Start creating big table.')
    events = [
        'play_video',
        'pause_video',
        'load_video',
        'edx.special_exam.proctored.attempt.started',
        'edx.ui.lms.outline.selected'
    ]

    print('Start writing the data to file.')
    table_headers = ['username']
    table_headers_top = ['']
    for page in page_names:
        for event in events:
            table_headers.append(event)
            table_headers_top.append(page)

    res_dict = {}
    for line in result:
        key = "{},{},{}".format(line[0], line[2], line[1],)
        res_dict[key] = line[3]

    # write to xlsx
    workbook = xlsxwriter.Workbook(result_file + '.xlsx')
    worksheet = workbook.add_worksheet()
    bold = workbook.add_format({'bold': True})

    with open(result_file + '.csv', mode="a", encoding="utf-8") as file:
        writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        # write to csv
        writer.writerow(table_headers_top)
        writer.writerow(table_headers)

        # write to xlsx
        # table_headers_top_tuple = tuple(table_headers_top)
        table_headers_tuple = tuple(table_headers)
        # worksheet.write_row(0, 0, table_headers_top)
        worksheet.write_row(1, 0, table_headers)

        i = 2
        array = []
        for user in user_names:
            one_line = [user[0]]

            for page in page_names:
                for event in events:
                    key = "{},{},{}".format(user[0], page[0], event)
                    if key in res_dict:
                        one_line.append(res_dict[key])
                    else:
                        one_line.append(0)

            # write to xlsx one by line
            one_tuple_line = tuple(list(one_line))
            worksheet.write_row(i, 0, one_tuple_line)

            # write to csv
            array.append(one_line)
            i = i + 1
            if i > 100:
                writer.writerows(array)
                array = []

        # write to csv
        writer.writerows(array)

        workbook.close()


def generate_figure(user_names):
    pass


def main(argv):
    print('Start calculating unique user names.')

    database_name = argv[1]
    user_name = argv[2]
    result_file = argv[3]

    connection = open_db_connection(database_name, user_name)
    page_names = get_all_pages_names(connection)
    user_names = get_all_users(connection)
    users_events_by_pages = calculate_users_and_ids(connection)
    # write_result_to_file(result_file, users_events_by_pages)
    write_result_to_table_file(result_file, users_events_by_pages, page_names, user_names)
    print('The analytics result can be found at ', result_file)
    close_db_connection(connection)


if __name__ == '__main__':
    main(sys.argv)
