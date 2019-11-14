import sys
import datetime
import pandas as pd
import re
from urllib.parse import unquote

# NOTE: Appending module from the folder above.
sys.path.append("../scripts/")
from database_services import *


"""
* Retrieves unique course IDs from the connected database.
* @param connection - connection to the target database;
* @returns list of unique courses' IDs;
"""
def get_unique_course_ids(connection):
    unique_course_id_query = '''
    SELECT DISTINCT (log_line ->> 'context')::json ->> 'course_id' AS course_identifier 
    FRO, logs ORDER BY course_identifier
    '''
    connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = connection.cursor()
    cursor.execute(unique_course_id_query)
    unique_course_ids = cursor.fetchall()
    cursor.close()
    connection.commit()
    return unique_course_ids


""" 
* Fetches distribution of the courses' enrollment.
* @returns map - course ID and enrollment time. Not that course ID is not distinct.
"""
def get_enrollment_distribution(connection):
    enrollment_distribution_sql_request = ''' 
    SELECT uniqueCourseIds.identifier as course_identifier, AVG(uniqueCourseIds.target_time) as course_time from (
        SELECT (log_line ->> 'context')::json ->> 'course_id' AS identifier,
        to_timestamp(log_line ->> 'time', 'YYYY-MM-DD"T"HH24:MI:SS')::TIME AS target_time
        FROM logs 
    ) uniqueCourseIds GROUP BY course_identifier
    '''

    connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = connection.cursor()
    cursor.execute(enrollment_distribution_sql_request)
    enrollment_distribution_course_id_and_time = cursor.fetchall()
    cursor.close()
    connection.commit()
    return enrollment_distribution_course_id_and_time

"""
* Retrieves average time to enroll any course.
* @param connection - connection to the target database;
 *@returns average time to enroll any course;
"""
def get_average_time_to_enroll_any_course(connection):
    # NOTE: Getting average time to enroll the course based on every enrolling event.
    total_average_time_to_enroll_course = '''
        SELECT enrolling_events.target_time from (
            SELECT avg(to_timestamp(log_line ->> 'time', 'YYYY-MM-DD"T"HH24:MI:SS')::TIME) as target_time
            FROM logs 
            WHERE log_line ->> 'event_type' LIKE '%.activated'
        ) enrolling_events
    '''
    
    connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = connection.cursor()
    cursor.execute(total_average_time_to_enroll_course)
    average_time_to_enroll = cursor.fetchall()
    cursor.close()
    connection.commit()
    return average_time_to_enroll

def generate_heatmap(x_values, y_values, z_values):
    enrollment_distribution_heatmap = go.Figure(data=go.Heatmap(
        z=z_values,
        x=x_values,
        y=y_values)
    )
    enrollment_distribution_heatmap.update_layout(
        title="Course enrollment statistics",
        xaxis_nticks=10,
        xaxis_title="Time, minutes",
        yaxis_title="Amount of peoople enrolled"
    )




def main(argv):
    print('Start calculating page activity on course distributed by day.')

    # NOTE: Mocking credentials while debugging.
    database_name = "OpenEduDatabase"
    user_name = "OPENEDU"

    connection = open_db_connection(database_name, user_name)
    average_time_to_enroll_any_course = get_enrollment_distribution(connection)
    print('Average time of the day to get enrolled into the course is {}'.format(average_time_to_enroll_any_course))
    close_db_connection(connection)


if __name__ == '__main__':
    main(sys.argv)

