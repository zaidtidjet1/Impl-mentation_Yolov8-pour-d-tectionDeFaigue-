# import all required library

import cv2
from django.http import StreamingHttpResponse
from django.views.decorators import gzip
from django.shortcuts import render
from ultralytics import YOLO
from rest_framework.response import Response
from django.utils.cache import add_never_cache_headers

# import yolo model
model = YOLO("./static/video/yolov8m.pt")

# Global variable to indicate whether streaming should continue or not
streaming_active = True

# function to render index template
def index(request):
    return render(request, "index.html")

@gzip.gzip_page
def video_feed_live(request):
    global streaming_active
    streaming_active = True  # Ensure streaming is active when starting
    response = StreamingHttpResponse(stream("live"), content_type='multipart/x-mixed-replace; boundary=frame')
    add_never_cache_headers(response)  # Prevent caching
    return response

# This view function handles the video file streaming
@gzip.gzip_page
def video_feed(request):
    global streaming_active
    streaming_active = True  # Ensure streaming is active when starting
    response = StreamingHttpResponse(stream("video"), content_type='multipart/x-mixed-replace; boundary=frame')
    add_never_cache_headers(response)  # Prevent caching
    return response

# This generator function streams frames from either a live camera or a video file, based on the mode parameter
def stream(mode):
    if mode == "live":
        cap = cv2.VideoCapture(0)  # Capture video from webcam
    else:
        video_path = "./static/video/video1.mp4"  # Path to video file
        cap = cv2.VideoCapture(video_path)  # Capture video from file

    while streaming_active:
        success, frame = cap.read()  # Read a frame from the video stream
        if success:
            # You can perform any processing on the frame here (commented out for now)
            # For example, apply YOLO object detection using the 'model' object
            frame = model.predict(frame, imgsz=640, conf=0.5)
            frame = frame[0].plot()
            # pass
        else:
            break  # Break the loop if no more frames are available

        _, jpeg = cv2.imencode('.jpg', frame)  # Encode the frame as JPEG
        frame = jpeg.tobytes()  # Convert the frame to bytes
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # Yield the frame for streaming

    cap.release()  # Release the video capture object when streaming is stopped

# This view function stops the streaming by setting streaming_active to False
def stop_streaming(request):
    global streaming_active
    streaming_active = False
    return render(request, "index.html")  # You can redirect to any other page after stopping the stream