FROM python:3.6

WORKDIR /face_recognition

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
COPY requirements.txt .
COPY ./antispoofing_models ./antispoofing_models
COPY ./faces ./faces
COPY ./models ./models
COPY detection.py .
COPY livelines_net.py .
COPY liveness_net_speed_check.py .
COPY database.py .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "livelines_net.py"]