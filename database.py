# Import necessary libraries
import psycopg2
from datetime import datetime
import notification
import os
# Define the PostgreSQL database connection parameters
db_params = {
    'dbname': 'Accounting_system',
    'user': 'postgres',
    'password': 'nur123',
    'host': 'localhost',
    #'host': os.environ.get('HOST', 'localhost'),
    'port': 5432
}
#192.168.56.1
def storing_face_encodings(name, surname, encoding):
    try:
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()

        # Create a table if it doesn't exist
        create_table_query = '''
            CREATE TABLE IF NOT EXISTS known_faces (
                id SERIAL PRIMARY KEY,
                name TEXT,
                surname TEXT,
                encoding BYTEA
            )
        '''
        cursor.execute(create_table_query)
        # Convert the NumPy array to bytes
        encoding_bytes = encoding.tobytes()

        # Insert data into the table
        insert_query = '''
            INSERT INTO known_faces (name, surname, encoding)
            VALUES (%s, %s, %s)
        '''
        cursor.execute(insert_query, (name, surname, encoding_bytes))
        conn.commit()

        cursor.close()
        conn.close()
        return True  # Return True to indicate success
    except Exception as e:
        print(e)
        return False  # Return False to indicate an error


def load_known_faces_from_database():
    try:
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()

        # Select all encodings, names, and surnames from the table
        select_query = '''
            SELECT encoding, name, surname
            FROM known_faces
        '''
        cursor.execute(select_query)
        records = cursor.fetchall()

        # Iterate through the records and add them to the known_face_encodings and known_face_names lists
        cursor.close()
        conn.close()
        return records  # Return True to indicate success
    except Exception as e:
        print(e)
        return False  # Return False to indicate an error

# Create a function to record arrival time in the database
def record_arrival(name, surname):
    try:

        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()


        # Get the current date and time
        arrival_time = datetime.now()
        print(arrival_time)
        hour = arrival_time.hour
        minute = arrival_time.minute
        if hour > 8 or (hour == 8 and minute > 5):
            notification.send_late_notification()
            cursor.execute("INSERT INTO latecomers (name, surname, arrival_time) VALUES (%s, %s, %s)",
                           (name, surname, arrival_time))

        # Insert the arrival record into the database
        cursor.execute("INSERT INTO arrival_records (name, surname, arrival_time) VALUES (%s, %s, %s)",
                       (name, surname, arrival_time))

        conn.commit()
        cursor.close()
        conn.close()

        return True

    except Exception as e:
        print(e)
        return False
def get_arrivals():
    try:
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()

        select_query = '''
        SELECT name, surname, arrival_time
        FROM arrival_records
                '''
        cursor.execute(select_query)
        records = cursor.fetchall()

        # Iterate through the records and add them to the known_face_encodings and known_face_names lists
        cursor.close()
        conn.close()
        return records
    except Exception as e:
        print(e)
        return False
def get_latecomers():
    try:
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()

        select_query = '''
        SELECT name, surname, arrival_time
        FROM latecomers
                '''
        cursor.execute(select_query)
        records = cursor.fetchall()

        # Iterate through the records and add them to the known_face_encodings and known_face_names lists
        cursor.close()
        conn.close()
        return records
    except Exception as e:
        print(e)
        return False


# Define a route to handle POST requests for recording arrival time
