import datetime
import sys

from dateutil import parser
from database_services import *

# Prints results to the result directory
def print_result(user_times, months, result_file):
    with open(result_file, "w") as log_fh:
        log_fh.write("username")
        for month in months:
            log_fh.write(",time in " + str(month) + " month")
        log_fh.write(",total time")
        log_fh.write("\n")

        for user_time in user_times:
            log_fh.write(user_time[0])
            month_durations = user_time[1]
            for month_duration in month_durations:
                log_fh.write("," + str(month_duration.total_seconds() // 60))
            log_fh.write(str(sum(month_durations, datetime.timedelta()).total_seconds() // 60))
            log_fh.write("\n")


# Calculates total-video-watch-time-durations for every user from DB data
def calculate_times_for_users(play_pause_events, months):

    course_duration_in_months = len(months)

    # The dict matching username and his total time duration of video watching
    user_times = dict()
    # The auxiliary dict for storing current last played time for user (it's needed in processing)
    user_played_times = dict()

    last_play_video_session = ""
    print("Calculating times started")

    for event in play_pause_events:
        event_type = event[0]
        username = event[1]
        time = event[2]
        session = event[3]

        if event_type != "play_video" and event_type != "pause_video":
            continue

        cur_time = parser.parse(time)

        if username not in user_times:
            user_times[username] = [datetime.timedelta()] * course_duration_in_months
            user_played_times[username] = cur_time
        elif event_type == "play_video":
            user_played_times[username] = cur_time
            last_play_video_session = session
        elif session == last_play_video_session:
            # Check that last play_video event was emitted within the same session with current pause_video event
            # (e.g. not in the session some days ago - to avoid incorrect large timedelta values)
            user_times[username][months.index(cur_time.month)] += cur_time - user_played_times[username]

    return user_times

def get_result_from_db(connection):
    # Get all play and pause events from video_events table	
    get_play_pause_events_query = ''' SELECT log_line ->> 'event_type' as event_t, 
	                                         log_line -> 'username' as username,
											 log_line -> 'time' as time,
											 log_line -> 'session' as session
	    							  FROM logs 
									  WHERE log_line ->> 'event_type' = 'pause_video' OR 
		    						        log_line ->> 'event_type' = 'play_video' 
		    						  ORDER BY time ASC '''

    connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = connection.cursor()
    cursor.execute(get_play_pause_events_query)
    play_pause_events = cursor.fetchall()
    cursor.close()
    connection.commit()
	
    return play_pause_events

# Doing the analytic task (get users' video-watching durations)
def execute_analytics_task(result_from_db, result_file):
    # Get dict of users and their total video watching time values
    # Time is represented as datetime.timedelta type

    first_record_month = parser.parse(result_from_db[0][2]).month
    last_record_month = parser.parse(result_from_db[-1][2]).month

    # Creating months array for course months
    i = first_record_month
    months = []
    while i != last_record_month:
        if i > 12:
            i = 1
            continue
        months.append(i)
        i += 1
    months.append(last_record_month)

    user_times = calculate_times_for_users(result_from_db, months)

    # Sort users by their time video watching descending
    user_times = sorted(user_times.items(), key=lambda x : sum(x[1], datetime.timedelta()), reverse=True)
    # Print results of analytics task as table
    print_result(user_times, months, result_file)
    print('The analytics result can be found at ', result_file)


def main(argv):
    print("Analytics task started...")

    database_name = argv[1]
    user_name = argv[2]
    result_file = argv[3]

    connection = open_db_connection(database_name, user_name)
    result_from_db = get_result_from_db(connection)
    execute_analytics_task(result_from_db, result_file)
    close_db_connection(connection)


if __name__ == '__main__':
    main(sys.argv)