import pickle
import cv2
import mediapipe as mp
import numpy as np
from tensorflow.keras.models import load_model

model = load_model('asl.h5')
cap = cv2.VideoCapture(0)

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

hands = mp_hands.Hands(static_image_mode=False, min_detection_confidence=0.3)

# Alphabet Labels
labels_dict = {0: 'A', 1: 'B', 2: 'C', 3: 'D', 4: 'E',
               5:'F', 6: 'G', 7:'H', 8:'I', 9:'J',
               10: 'K', 11: 'L', 12: 'M', 13: 'N', 14: 'O',
               15:'P', 16:'Q', 17: 'R', 18:'S', 19:'T', 20:'U', 21:'V',
               22:'W', 23:'X',24:'Y', 25:'Z', 26: 'del', 27:'unknown', 28: 'space'}  # Adjust this based on your dataset

while True:
    data_aux = []
    x_ = []
    y_ = []

    ret, frame = cap.read()
    if not ret:
        break

    H, W, _ = frame.shape
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = hands.process(frame_rgb)

    #Get landmarks for hand
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                frame,  
                hand_landmarks, 
                mp_hands.HAND_CONNECTIONS,  
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style())

            # Extract the hand landmarks and normalize the coordinates
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
            print("Reshaped data_input:", data_input.shape)

            #Predict character using asl.h5 model
            prediction = model.predict(data_input)
            predicted_label = np.argmax(prediction, axis=1)[0]

            if predicted_label in labels_dict:
                print(f"Predicted Label: {predicted_label}")
                predicted_character = labels_dict[predicted_label]
                print(f"Predicted character: {predicted_character}")
            else:
                print(f"Warning: Predicted label {predicted_label} not found in labels_dict")
                predicted_character = "Unknown"  

            # Draw the bounding box and display the predicted character
            x1 = int(min(x_) * W) - 10
            y1 = int(min(y_) * H) - 10
            x2 = int(max(x_) * W) - 10
            y2 = int(max(y_) * H) - 10

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 0), 4)
            cv2.putText(frame, predicted_character, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 0, 0), 3,
                        cv2.LINE_AA)

    # Display the frame
    cv2.imshow('frame', frame)

    # Exit loop on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
