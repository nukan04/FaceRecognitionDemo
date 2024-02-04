import cv2
from tensorflow.keras.preprocessing.image import img_to_array
import os
import numpy as np
from tensorflow.keras.models import model_from_json
import time
# import detection
import database
import face_recognition

root_dir = os.getcwd()

# Load Face Detection Model
face_cascade = cv2.CascadeClassifier("models/haarcascade_frontalface_default.xml")

# Load Anti-Spoofing Model graph
json_file = open('antispoofing_models/antispoofing_model.json', 'r')
loaded_model_json = json_file.read()
json_file.close()
model = model_from_json(loaded_model_json)

# Load antispoofing model weights
model.load_weights('antispoofing_models/antispoofing_model.h5')
print("Model loaded from disk")

known_face_encodings = []
known_face_names = []


def load_known_faces():
    records = database.load_known_faces_from_database()
    for record in records:
        encoding_bytes, name, surname = record
        encoding_np_array = np.frombuffer(encoding_bytes, dtype=np.float64)
        known_face_encodings.append(encoding_np_array)
        known_face_names.append(f"{name}_{surname}")

# Insert new faces to database

confidence_threshold = 0.45  # Adjust this value as needed
# Load known faces from a database and insert new faces to database
known_faces_dir = "faces"
load_known_faces()
temp_name = "$"
def send(frame):
    global temp_name
    # Find all face locations and encodings in the current frame
    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, face_locations)
    if len(face_locations) < 1:
        print("there is no face here")
        return
    if len(face_locations) > 1:
        print("more than 1 face here")
        return
    name = "Unknown"
    # Loop through each face in the frame
    for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
        # Compare the current face encoding with known face encodings
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        min_distance = min(face_distances)


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
            #from here to
            print("here", name)
            print(" temp_name:", temp_name)

            if (temp_name != name):
                print(time.time(), name)
                database.record_arrival(first_name, last_name)
                temp_name = name
            #to here some bug if no work becouse of that we cant record arrivals
    return name

video = cv2.VideoCapture(0)

start_time = None
real_count = 0
threshold = 2  # Threshold for 2 seconds

while True:
    try:
        ret, frame = video.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            face = frame[y - 5:y + h + 5, x - 5:x + w + 5]
            resized_face = cv2.resize(face, (160, 160))
            resized_face = resized_face.astype("float") / 255.0
            resized_face = np.expand_dims(resized_face, axis=0)

            preds = model.predict(resized_face)[0]
            if preds > 0.5:
                label = 'spoof'
                cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
                start_time = None
            else:
                label = "not spoof"
                color = (0, 255, 0)
                if start_time is None:
                    start_time = time.time()
                else:
                    elapsed_time = time.time() - start_time
                    if elapsed_time >= threshold:
                        real_count += 1
                        if real_count >= 2:
                            label = send(frame)
                            real_count = 0
                cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
        print(label)
        cv2.imshow('Video', frame)
        key = cv2.waitKey(1)
        if key == ord('q'):
            break
    except Exception as e:
        pass

video.release()
cv2.destroyAllWindows()
