from flask import Flask, request, send_from_directory
from flask_socketio import SocketIO
from flask_cors import CORS
import os

import datetime
import cv2
import mediapipe as mp
import numpy as np
from tensorflow.keras.models import load_model

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, max_http_buffer_size=1e8, cors_allowed_origins="*" )

'''
Debug statement to determine if a
client has connected to server
'''
@socketio.on("connect")
def connect():
    print("Connected")


'''
Event that receives ASL video and exports it to mp4,
Translates each frame of the video to a letter 

Sends back the full word from the video back to the client
'''
@socketio.on("message")
def message(message, sid):
    print(sid)
    file_name = message.get("fileName", "unnamed.mp4")
    buffer = message["buffer"]

    file_path = os.path.join("./ASL Videos")

    if not os.path.exists(file_path):
        os.mkdir(file_path)

    with open(os.path.join(file_path, file_name), "wb") as f:
        f.write(buffer)

    word = extract_frames("./ASL Videos/test.mp4")
   
    if os.path.exists("./ASL Videos/test.mp4"):
        os.remove("./ASL Videos/test.mp4")
    else:
        print("The file does not exist")
    socketio.emit("message", (word, sid), include_self=True)



'''
Extracts frames at a rate of 'frame_rate' and uses the asl.h5 model 
to predict what the current handsign is

Joins all the predicted labels and returns the full word.
'''
def extract_frames(video_path, frame_rate=25):
    first = datetime.datetime.now()
    print(first)
    labels_dict = {0: 'A', 1: 'B', 2: 'C', 3: 'D', 4: 'E',
               5:'F', 6: 'G', 7:'H', 8:'I', 9:'J',
               10: 'K', 11: 'L', 12: 'M', 13: 'N', 14: 'O',
               15:'P', 16:'Q', 17: 'R', 18:'S', 19:'T', 20:'U', 21:'V',
               22:'W', 23:'X',24:'Y', 25:'Z'}  

    vidcap = cv2.VideoCapture(video_path)
    success, image = vidcap.read()
    count = 0

    mp_hands = mp.solutions.hands

    hands = mp_hands.Hands(static_image_mode=False, min_detection_confidence=0.3)
    word = []
    
    while success:
        data_aux = []
        x_ = []
        y_ = []

        blurs = []
        
        results = hands.process(image)

        if results.multi_hand_landmarks:
            cv2.imwrite(f"./ASL Videos/all/{count}.jpg", image)
            if count % frame_rate == 0:
                for hand_landmarks in results.multi_hand_landmarks:
                    for i in range(len(hand_landmarks.landmark)):
                        x = hand_landmarks.landmark[i].x
                        y = hand_landmarks.landmark[i].y

                        x_.append(x)
                        y_.append(y)

                    x_min = int(min(x_) * image.shape[1])
                    y_min = int(min(y_) * image.shape[0])
                    x_max = int(max(x_) * image.shape[1])
                    y_max = int(max(y_) * image.shape[0])

                    # Crop the hand region
                    
                    hand_image = image[y_min-10:y_max+10, x_min-10:x_max+10]
                    gray = cv2.cvtColor(hand_image, cv2.COLOR_BGR2GRAY)
                    blur = getBlur(gray)
                    threshold = 150
                    print(count , " " , blur)
                    # cv2.imwrite(f"./ASL Videos/all/{count}.jpg", gray)

                    if(blur > threshold):
                        cv2.imwrite(f"./ASL Videos/good/{count}.jpg", gray)

                        for i in range(len(hand_landmarks.landmark)):
                            x = hand_landmarks.landmark[i].x
                            y = hand_landmarks.landmark[i].y
                            data_aux.append(x - min(x_))
                            data_aux.append(y - min(y_))


                        if len(data_aux) == 42 :
                            print("IN HERE")
                            data_input = np.array(data_aux).reshape(1, 21, 2, 1)

                            prediction = model.predict(data_input)
                            print(prediction)
                            predicted_label = np.argmax(prediction, axis=1)[0]
                            print(predicted_label)
                            if predicted_label in labels_dict:
                                predicted_character = labels_dict[predicted_label]
                                # cv2.imwrite(f"./ASL Videos/frame{count}.jpg", image)
                                
                                word.append(predicted_character)
                            else:
                                print(f"Warning: Predicted label {predicted_label} not found in labels_dict")
                                predicted_character = "Unknown" 
                    else:
                        print(f'{count} is blurry : {blur}')
                        cv2.imwrite(f"./ASL Videos/passed/{count}.jpg", gray)

            count += 1
        success, image = vidcap.read()

    second = datetime.datetime.now()
    print("".join(word))
    print(second- first)
    print(word)

    return "".join(word)


def getBlur(image):
	# compute the Laplacian of the image and then return the focus
	# measure, which is simply the variance of the Laplacian
	return cv2.Laplacian(image, cv2.CV_64F).var()



if __name__ == "__main__":
    # vd = Video()
    model = load_model('asl.h5')
    socketio.run(app, host='0.0.0.0', port=8080)