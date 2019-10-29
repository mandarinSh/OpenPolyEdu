import datetime
import json
import sys
from database_services import *

# Gets datetime object from log 'time' string
def parse_datetime(log_timestamp):
    dt = log_timestamp.split("T")
    date = dt[0].split("-")
    time = dt[1].split(".")[0].split(":")
    return datetime.datetime(int(date[0]), int(date[1]), int(date[2]), hour=int(time[0]), minute=int(time[1]), second=int(time[2]))

# Prints results to the result directory
def print_result(user_times, result_file):
    log_fh = open(result_file, "w")
    log_fh.write("username,time(sec)\n")
    for username in user_times:
        log_fh.write(username + "," +  str(user_times[username].total_seconds()) + "\n")
    log_fh.close()


# Calculates total-video-watch-time-durations for every user from DB data
def calculate_times_for_users(play_pause_events):

    # The dict matching username and his total time duration of video watching
    user_times = dict()
    # The auxiliary dict for storing current last played time for user (it's needed in processing)
    user_played_times = dict()

    for event in play_pause_events:
        event_type = event[0]
        username = event[1]
        time = event[2]

        if event_type != "play_video" and event_type != "pause_video":
            continue

        cur_time = parse_datetime(time)
    
        if username not in user_times:
            user_times[username] = datetime.timedelta()
            user_played_times[username] = cur_time
        elif event_type == "pause_video":
            user_times[username] += cur_time - user_played_times[username]
        else:
            user_played_times[username] = cur_time

    return user_times


# Doing the analytic task (get users' video-watching durations)
def do_task(connection, result_file):

    # Get all play and pause events from video_events table	
    get_play_pause_events_query = ''' SELECT log_line ->> 'event_type' as event_t, log_line -> 'username' as username, log_line -> 'time' as time 
	    							  FROM logs WHERE log_line ->> 'event_type' = 'pause_video' OR 
		    						  log_line ->> 'event_type' = 'play_video' '''

    connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = connection.cursor()
    cursor.execute(get_play_pause_events_query)
    play_pause_events = cursor.fetchall()
    cursor.close()
    connection.commit()
	
    # Get dict of users and their total video watching time values
    # Time is represented as datetime.timedelta type
    user_times = calculate_times_for_users(play_pause_events)

    # Print results of analytics task as table
    print_result(user_times, result_file)
    print('The analytics result can be found at ', result_file)


def main(argv):
    print("Start calculating users' video watching time durations")

    database_name = argv[1]
    user_name = argv[2]
    result_file = argv[3]

    connection = open_db_connection(database_name, user_name)
    do_task(connection, result_file)
    close_db_connection(connection)


if __name__ == '__main__':
    main(sys.argv)