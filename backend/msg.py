from flask import Flask, request, send_from_directory
from flask_socketio import SocketIO
from flask_cors import CORS
import os

import datetime
import cv2
import mediapipe as mp
import numpy as np
from tensorflow.keras.models import load_model

from skimage.metrics import structural_similarity as ssim


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
def message(message, sid, speed):
    # print(sid)
    file_name = message.get("fileName", "unnamed.mp4")
    buffer = message["buffer"]

    file_path = os.path.join("./ASL Videos")

    if not os.path.exists(file_path):
        os.mkdir(file_path)

    with open(os.path.join(file_path, file_name), "wb") as f:
        f.write(buffer)

    print(speed)
    word = extract_frames("./ASL Videos/test.mp4", int(speed))
    #print(word)
    if os.path.exists("./ASL Videos/test.mp4"):
        os.remove("./ASL Videos/test.mp4")
    else:
        print("The file does not exist")
    socketio.emit("message", (word, sid), include_self=True)

@socketio.on("textMessage")
def textMessage(message, sid):
    socketio.emit("textMessage", (message, sid), include_self=True)


'''
Returns the laplacion variance
This is used to decide how blurry an image is
'''
def getBlur(image):
	return cv2.Laplacian(image, cv2.CV_64F).var()



'''
Isolates the image of the hand and gets the blurriness of the image.
Values are later used to compare the bluriness of each frame 
and makes a prediction on the sharpess frame in the frame_rate
'''
def get_hand(image, results, count):
    blur = 0

    for hand_landmarks in results.multi_hand_landmarks:
        # Extract the 2D landmark points
        h, w, _ = image.shape  # Image dimensions
        landmark_points = [(int(landmark.x * w), int(landmark.y * h)) for landmark in hand_landmarks.landmark]

        # Calculate the bounding box
        x_coords = [point[0] for point in landmark_points]
        y_coords = [point[1] for point in landmark_points]
        x_min, x_max = max(0, min(x_coords)), min(w, max(x_coords))
        y_min, y_max = max(0, min(y_coords)), min(h, max(y_coords))

        padding = 20
        x_min = max(0, x_min - padding)
        x_max = min(w, x_max + padding)
        y_min = max(0, y_min - padding)
        y_max = min(h, y_max + padding)

        hand_image = image[y_min:y_max, x_min:x_max]
        # gray = cv2.cvtColor(hand_image, cv2.COLOR_BGR2GRAY)
        # equalized_image = cv2.equalizeHist(gray)

        # print(avg_brightness)

        blur = getBlur(image)

    # cv2.imwrite(f"./ASL Videos/all/equal{count}.jpg", equalized_image)
    # cv2.imwrite(f"./ASL Videos/all/norm{count}.jpg", gray)
        # return blur, hand_image

    return blur, image

'''
Gets the hands of the clearest image and extracts the hand landmarks,
sends the hand landmarks to a prediction model to predict what 
ASL hand sign is being made
'''
def predict_letter(res):
    # print("THIS IS LETTER")
    data_aux = []
    x_ = []
    y_ = []
    labels_dict = {0: 'A', 1: 'B', 2: 'C', 3: 'D', 4: 'E',
               5:'F', 6: 'G', 7:'H', 8:'I', 9:'J',
               10: 'K', 11: 'L', 12: 'M', 13: 'N', 14: 'O',
               15:'P', 16:'Q', 17: 'R', 18:'S', 19:'T', 20:'U', 21:'V',
               22:'W', 23:'X',24:'Y', 25:'Z', 26: 'del', 27:'unknown', 28: 'space'} 
    
    for hand_landmarks in res.multi_hand_landmarks:
        for i in range(len(hand_landmarks.landmark)):
            x = hand_landmarks.landmark[i].x
            y = hand_landmarks.landmark[i].y

            x_.append(x)
            y_.append(y)
    

        for i in range(len(hand_landmarks.landmark)):
            x = hand_landmarks.landmark[i].x
            y = hand_landmarks.landmark[i].y
            data_aux.append(x - min(x_))
            data_aux.append(y - min(y_))


        if len(data_aux) == 42 :
            print("IN HERE")
            data_input = np.array(data_aux).reshape(1, 21, 2, 1)

            prediction = model.predict(data_input)
            predicted_label = np.argmax(prediction, axis=1)[0]
            if predicted_label in labels_dict:
                predicted_character = labels_dict[predicted_label]
                return predicted_character
            
    return "Unknown" 

'''
Extracts frames at a rate of 'frame_rate' and uses the asl.h5 model 
to predict what the current handsign is

Joins all the predicted labels and returns the full word.
'''
def extract_frames(video_path, frame_rate=12):
    first = datetime.datetime.now()
    print(first)
    

    vidcap = cv2.VideoCapture(video_path)
    success, image = vidcap.read()

    count = 0

    mp_hands = mp.solutions.hands

    hands = mp_hands.Hands(
        max_num_hands=1,  
        min_detection_confidence=0.25, 
    )
    word = []

    max_blurscore = 0
    clear_image = image
    
    while success:
        results = hands.process(image)
        if results.multi_hand_landmarks:
            blur_score, img = get_hand(image, results, count)

            print(count, blur_score)
            cv2.imwrite(f"./ASL Videos/all/hand{count}.jpg", img)

            if blur_score > max_blurscore and blur_score > 200:
                max_blurscore = blur_score
                clear_image = img
                max_index = count

            count += 1

            if count % frame_rate == 0:
                temp = hands.process(clear_image)
                if temp.multi_hand_landmarks:
                    cv2.imwrite(f"./ASL Videos/good/{max_index}____{max_blurscore}.jpg", clear_image)
                    letter = predict_letter(temp)
                    if(letter == "space"):
                        word.append(" ")
                    elif(letter != "Unknown"):
                        word.append(letter)
                    max_blurscore = 0
                    clear_image = 0

            
        
        success, image = vidcap.read()

    print(count)
       
    return "".join(word)

if __name__ == "__main__":
    model = load_model('asl.h5')
    socketio.run(app, host='0.0.0.0', port=8080)