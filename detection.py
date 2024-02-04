import face_recognition
import cv2
import numpy as np
import os
import database
import dlib

# Define the known face encodings and corresponding names
known_face_encodings = []
known_face_names = []

temp_name = 'Nur'
temp_surname = 'Kazbekov'

# Load images of known people and their encodings
def load_known_faces():
    records = database.load_known_faces_from_database()
    for record in records:
        encoding_bytes, name, surname = record
        encoding_np_array = np.frombuffer(encoding_bytes, dtype=np.float64)
        known_face_encodings.append(encoding_np_array)
        known_face_names.append(f"{name}_{surname}")

# Insert new faces to database
def insert_to_database_faces(known_faces_dir):
    for filename in os.listdir(known_faces_dir):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            name = os.path.splitext(filename)[0]
            image_path = os.path.join(known_faces_dir, filename)
            image = face_recognition.load_image_file(image_path)
            encoding = face_recognition.face_encodings(image)[0]
            first_name, last_name = name.split('_', 1)
            if any(np.all(encoding == known_face_encoding) for known_face_encoding in known_face_encodings):
                continue
            database.storing_face_encodings(first_name, last_name, encoding)

# Set the confidence threshold
confidence_threshold = 0.45
# Adjust this value as needed

# Initialize the video capture
video_capture = cv2.VideoCapture(0)  # 0 for default camera (change if needed)
if not video_capture.isOpened():
    print("Error: Could not open webcam.")


# Load known faces from a database and insert new faces to database
known_faces_dir = "faces"
load_known_faces()
#insert_to_database_faces(known_faces_dir)
detector = dlib.get_frontal_face_detector()

while True:
    # Capture a single frame from the video feed
    ret, frame = video_capture.read()

    # Find all face locations and encodings in the current frame
    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, face_locations)

    # Loop through each face in the frame
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        # Compare the current face encoding with known face encodings
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        min_distance = min(face_distances)
        name = "Unknown"

        face_image = frame[top:bottom, left:right]

        # Classify the face as real or photo
        #is_real_face = classify_face_as_real_or_photo(face_image)
        if min_distance <= confidence_threshold: #and is_real_face :
            # Find the index of the closest match
            match_index = np.argmin(face_distances)
            name = known_face_names[match_index]
            first_name, last_name = name.split('_', 1)

            # Send a JSON POST request to the server
            data = {
                "name": first_name,
                "surname": last_name
            }
            print(data)
            if (first_name != temp_name and last_name != temp_surname): database.record_arrival(first_name, last_name)
            temp_name = first_name
            temp_surname = last_name
        else:
            name = "Unknown"
            is_real_face = False

    # Exit the loop by pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture and close all windows
video_capture.release()
cv2.destroyAllWindows()
