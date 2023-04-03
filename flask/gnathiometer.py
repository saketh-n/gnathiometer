from flask import Flask, request, jsonify, Response
from flask_cors import CORS, cross_origin
from flask_socketio import SocketIO
import base64
import cv2
import numpy as np
import os

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="http://localhost:3000")
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/api/process-image', methods=['POST'])
@cross_origin()
def process_image():
    # Receive the uploaded image
    file = request.files['image']
    image = cv2.imdecode(np.frombuffer(file.read(), np.uint8), cv2.IMREAD_COLOR)
    
    # Process the image using your Face Growth Guide functionality

    # Convert the image to grayscale for face detection
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Use OpenCV's Haar Cascade classifier to detect faces in the image
    current_directory = os.path.dirname(os.path.abspath(__file__))
    cascade_path = os.path.join(current_directory, 'haarcascade_frontalface_default.xml')
    face_cascade = cv2.CascadeClassifier(cascade_path)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=3, minSize=(30, 30))

    # Extract the ruler from the image using a combination of thresholding and contour detection
    gray_blur = cv2.GaussianBlur(gray, (15, 15), 0)
    thresh = cv2.threshold(gray_blur, 90, 255, cv2.THRESH_BINARY)[1]
    contours, hierarchy = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for c in contours:
        if cv2.contourArea(c) > 10000:
            #cv2.drawContours(image, [c], 0, (0, 255, 0), 3)
            break


    # Use the ruler to determine the scale of the image
    scale_pixels = cv2.arcLength(contours[0], True)
    scale_mm = 300 # change this value according to the actual size of the ruler in millimeters
    scale = scale_mm / scale_pixels

    # Extract the face from the image using the detected face bounding box
    print(len(faces))
    print(faces)
    for (x, y, w, h) in faces:
        print(x)
        print(y)
        cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)
        roi_gray = gray[y:y + h, x:x + w]
        roi_color = image[y:y + h, x:x + w]
        break

    # Overlay the growth guide over the face, scaled to life-size using the determined scale
    guide_path = os.path.join(current_directory, 'guide.png')
    guide = cv2.imread(guide_path)
    # Get the dimensions of the guide image
    guide_height, guide_width, _ = guide.shape

    # Calculate the new dimensions of the guide_scaled based on the guide's dimensions and scale
    new_guide_width = int(guide_width * scale)
    new_guide_height = int(guide_height * scale)

    # Resize the guide to the new dimensions
    guide_scaled = cv2.resize(guide, (new_guide_width, new_guide_height))

    # Overlay the guide_scaled on the image at the position of the detected face
    '''if len(faces):
        (x, y, w, h) = faces[0]
        roi = image[y:y + new_guide_height, x:x + new_guide_width]
        blended = cv2.addWeighted(roi, 1, guide_scaled, 0.5, 0)
        image[y:y + new_guide_height, x:x + new_guide_width] = blended'''

    
    # Encode the processed image as a base64 string
    _, buffer = cv2.imencode('.jpg', image)
    encoded_image = base64.b64encode(buffer).decode('utf-8')

    return Response(f"data:image/jpeg;base64,{encoded_image}", content_type='text/plain')

if __name__ == '__main__':
    app.run(debug=True)
