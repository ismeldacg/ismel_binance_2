import mysql.connector
from mysql.connector import Error



# create the connection
def create_connection(host_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name, user=user_name, passwd=user_password, database=db_name
        )

        # print("Connection to MySQL DB successful")
    except Error as e:
        # print(f"The error '{e}' occurred")
        connection = False
        return connection
    return connection

#execution of query
def execute_user_query(connection, aQuery):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(aQuery)
        result = cursor.fetchall()
        return result
    except Error as e:
        # fatal error
        print(f"The error '{e}' occurred")


#insert values in table
def insert_into_table(connection, aQuery, some_values):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(aQuery, some_values)
        result = cursor.fetchall()
        connection.commit()
        return result
    except Error as e:
        # fatal error
        print(f"The error '{e}' occurred")


