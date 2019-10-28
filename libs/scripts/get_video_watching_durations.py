import datetime
import json
import psycopg2


# Gets datetime object from log 'time' string
def parse_datetime(log_timestamp):
    dt = log_timestamp.split("T")
    date = dt[0].split("-")
    time = dt[1].split(".")[0].split(":")
    return datetime.datetime(int(date[0]), int(date[1]), int(date[2]), hour=int(time[0]), minute=int(time[1]), second=int(time[2]))


# Prints total time of video-watching for every user (as a table) into console
def print_result_to_stdout(user_times):
    print("username | time (sec)")
    for username in user_times:
        print(username, "|", user_times[username].total_seconds())

# Prints results to the system-logs directory
def print_result_to_system_logs(user_times):
    log_path = "../../system-logs/get_video_watching_durations.log"
    log_fh = open(log_path, "w")
    log_fh.write("username | time (sec)\n")
    for username in user_times:
        log_fh.write(username + " | " +  str(user_times[username].total_seconds()) + "\n")
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
def do_task(db_params):

    # Connecting to DB
    con = psycopg2.connect(
      database=db_params['database'],
      user=db_params['user'],
      password=db_params['password'],
      host=db_params['host'], 
    )
    cur = con.cursor()

    # Get all play and pause events from video_events table
    cur.execute("SELECT event_type, username, time FROM video_events WHERE event_type='pause_video' OR event_type='play_video'")
    # Get dict of users and their total video watching time values
    # Time is represented as datetime.timedelta type
    user_times = calculate_times_for_users(cur.fetchall())

    # Print results of analytics task as table
    print_result_to_stdout(user_times)
    print_result_to_system_logs(user_times)

    cur.close()
    con.close()


postgres_params = { 'database':"postgres",
      'user':"postgres",
      'password':"postgres",
      'host':"127.0.0.1" }

do_task(postgres_params)

