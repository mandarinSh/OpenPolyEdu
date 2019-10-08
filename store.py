import psycopg2


def open_db_connection():
    try:

        connection = psycopg2.connect(user="postgres",
                                      password="root",
                                      host="127.0.0.1",
                                      port="5432",
                                      database="log_registry")

        # cursor = connection.cursor()
        return connection

    except (Exception, psycopg2.Error) as error:
        print("Error while connecting to PostgreSQL", error)


def close_db_connection(connection):
    if connection:
        # cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")


def execute_query(connection, query):
    cursor = connection.cursor()
    cursor.execute(query)
    connection.commit()
    cursor.close()


def drop_table(connection, table):
    drop_table_query = '''DROP TABLE IF EXISTS {0};'''.format(table)
    cursor = connection.cursor()
    cursor.execute(drop_table_query)
