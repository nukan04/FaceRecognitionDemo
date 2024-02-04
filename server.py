from flask import Flask, request, jsonify, render_template
import database
import json
import os
import face_recognition
from werkzeug.utils import secure_filename  # Import secure_filename from werkzeug.utils

app = Flask(__name__)
@app.route('/add', methods=['GET'])
def handle_add():
    return render_template('./add_employee.html')
@app.route('/add-employee', methods=['POST'])
def handle_add_employee():
    try:
        if 'photo' in request.files:
            photo = request.files['photo']
            filename = secure_filename(photo.filename)
            if filename.endswith((".jpg", ".png")):
                name = os.path.splitext(filename)[0]
                image = face_recognition.load_image_file(photo)
                encoding = face_recognition.face_encodings(image)[0]
                first_name, last_name = name.split('_', 1)
                # Assuming database is a valid module with storing_face_encodings function
                database.storing_face_encodings(first_name, last_name, encoding)
                print("Nice!")
                return "Photo uploaded and processed successfully"
            else:
                return "Invalid file format. Please upload a JPG or PNG file.", 400
        else:
            return "No 'photo' field in the request.", 400
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route('/record-arrival', methods=['POST'])
def handle_record_arrival():
    data = request.get_json()

    name = data.get('name')
    surname = data.get('surname')

    if name and surname:
        if database.record_arrival(name, surname):
            return jsonify({'message': 'Arrival recorded successfully'}), 200
        else:
            return jsonify({'message': 'Error recording arrival'}), 500
    else:
        return jsonify({'message': 'Invalid data'}), 400

@app.route('/get-arrivals', methods=['get'])
def handle_get_arrivals():
    data = database.get_arrivals()
    return render_template('./index.html', arrival=data)
@app.route('/get-latecomers', methods=['get'])
def handle_get_latecomers():
    data = database.get_latecomers()
    return render_template('./latecomers.html', arrival=data)
@app.route('/test', methods=['get'])
def handle_get():
    return str(database.load_known_faces_from_database())

if __name__ == '__main__':
    app.run(debug=True)

