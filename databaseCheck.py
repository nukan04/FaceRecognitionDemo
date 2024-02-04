import psycopg2
from datetime import datetime
import os

# Define the PostgreSQL database connection parameters
db_params = {
    'dbname': 'Accounting_system',
    'user': 'postgres',
    'password': 'nur123',
    'host': 'localhost',
    'port': 5432
}

#192.168.56.1
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
print(load_known_faces_from_database())