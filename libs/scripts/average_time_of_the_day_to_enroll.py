import sys
import csv
from database_services import *


""" 
* Fetches distribution of the courses' enrollment.
* @returns map - course ID and enrollment time. Not that course ID is not distinct.
"""
def get_enrollment_distribution(connection):
    # NOTE: The result should generate a table with columns 'id' and 'average time to enroll'
    enrollment_distribution_sql_request = ''' 
    SELECT uniqueCourseIds.identifier as course_identifier, AVG(uniqueCourseIds.target_time) as course_time from (
        SELECT (log_line ->> 'context')::json ->> 'course_id' AS identifier,
        to_timestamp(log_line ->> 'time', 'YYYY-MM-DD"T"HH24:MI:SS')::TIME AS target_time
        FROM logs 
        WHERE log_line ->> 'event_type' LIKE '%enrollment.activated' 
    ) uniqueCourseIds GROUP BY course_identifier
    '''
    connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = connection.cursor()
    cursor.execute(enrollment_distribution_sql_request)
    enrollment_distribution_course_id_and_time = cursor.fetchall()
    cursor.close()
    connection.commit()
    return enrollment_distribution_course_id_and_time


def write_result_to_file(result_file, result):
    print('Start writing the data to file.')
    with open(result_file, mode='w', encoding='utf-8') as res_file:
        field_names = ['course_id', 'average time to enroll']
        result_file_writer = csv.writer(res_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        result_file_writer.writerow(field_names)
        for res in result:
            result_file_writer.writerow(res)


def main(argv):
    print('Start calculating average time to enroll the course.')
    
    database_name = argv[1]
    user_name = argv[2]
    result_file = argv[3]

    connection = open_db_connection(database_name, user_name)
    enrollment_distribution = get_enrollment_distribution(connection)
    close_db_connection(connection)

    write_result_to_file(result_file, enrollment_distribution)
    print(f'The result file could be found at {result_file}')


if __name__ == '__main__':
    main(sys.argv)

