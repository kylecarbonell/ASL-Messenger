import datetime
import pickle
import cv2
import mediapipe as mp
import numpy as np
from tensorflow.keras.models import load_model

import Katna

model = load_model('asl.h5')

def extract_frames(video_path, output_dir, frame_rate=1):
    first = datetime.datetime.now()
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
        results = hands.process(image)
        
        if results.multi_hand_landmarks:
            if count % frame_rate == 0:
                for hand_landmarks in results.multi_hand_landmarks:

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

                if len(data_aux) == 42:
                    data_input = np.array(data_aux).reshape(1, 21, 2, 1)

                    prediction = model.predict(data_input)
                    predicted_label = np.argmax(prediction, axis=1)[0]

                    if predicted_label in labels_dict:
                        predicted_character = labels_dict[predicted_label]
                        # cv2.imwrite(f"{output_dir}/frame{count}.jpg", image)
                        word.append(predicted_character)
                    else:
                        print(f"Warning: Predicted label {predicted_label} not found in labels_dict")
                        predicted_character = "Unknown"  # Handle unexpected predictions
                
            count += 1
        success, image = vidcap.read()

    second = datetime.datetime.now()
    print("".join(word))
    print(second- first)


if __name__ == "__main__":
    key = input("Press to read: ")
    while key !=
    # extract_frames("./test.mp4", "./frames", 30)


