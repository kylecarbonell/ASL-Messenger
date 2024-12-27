# ASL Messaging App

## Overview  
This project bridges the gap between American Sign Language (ASL) speakers and non-speakers by providing a functional ASL interpreter integrated into a messaging app. By leveraging computer vision, machine learning, and web technologies, the app identifies ASL hand signs and converts them into text, enabling seamless communication.

---

## Motivation  
Sign language is a unique and expressive form of communication, but the gap between ASL users and non-users can hinder interactions. This project aims to promote recognition of ASL and expand the ASL-speaking community by offering a tool that helps users understand and communicate using ASL more effectively.

---

## Features  
- **Real-Time ASL Interpretation**: Detects and predicts ASL hand signs with high accuracy.  
- **Messaging Functionality**: Allows users to send ASL signs as messages.  
- **Web Application**: Built with Svelte (frontend) and Flask (backend) for a smooth user experience.  
- **Frame Selection Logic**: Incorporates Laplacian variance and frame rate skipping to optimize hand sign detection in videos.  

---

## Technologies Used  

### Machine Learning
- **Model Architecture**: Convolutional Neural Network (CNN) with 8 layers.  
- **Dataset**:  
  - Initially used [Ayush Thakur’s ASL Dataset](https://www.kaggle.com/datasets/ayuraj/asl-dataset).  
  - Final model trained on [Akash Nagaraj’s ASL Alphabet Dataset](https://www.kaggle.com/datasets/grassknoted/asl-alphabet).  
- **Training**:  
  - Extracted hand landmarks using a hand-tracking library.  
  - Trained the CNN model with 150 epochs for optimal accuracy.  

### Web Development  
- **Frontend**: Built using Svelte for a responsive and clean user interface.  
- **Backend**: Flask with Socket.io for real-time communication between client and server.  
- **Video Handling**: Utilized the MediaRecorder library for video input and Laplacian variance for frame selection.

---

## Results  
- Achieved **99.7% training accuracy** and **99.6% testing accuracy**, with losses of 1.40% and 1.52%, respectively.  
- Produced a functional messaging app with accurate ASL interpretation.  
- Overcame challenges in identifying the correct frames for hand signs by implementing frame rate skipping and blur detection.

---

## Future Development  
- **Expanding ASL Vocabulary**: Incorporate more complex signs, including multi-hand and dynamic gestures.  
- **Dynamic Gesture Recognition**: Implement RNN architectures to process sequences of hand movements over time.  
- **Enhanced Frame Detection**: Refine the Laplacian variance and frame rate logic for better accuracy.  
- **Mobile Integration**: Adapt the application for mobile platforms to increase accessibility.

---

## Work Distribution  
- **Kyle**:  
  - Extracted hand landmarks from datasets.  
  - Trained the CNN model.  
  - Developed backend with Flask, including web sockets for real-time messaging.  
- **Karen**:  
  - Prepared hand data for training.  
  - Designed the frontend using Svelte.  
  - Implemented video recording and sending functionality.  
- **Collaborative**:  
  - Researched project ideas and methodologies.  
  - Created presentation slides and the project report.

---

## Installation and Usage  

### Prerequisites  
- Python 3.x  
- Node.js  
- Flask  
- Svelte  

### Steps  
1. **Clone the Repository**:  
   ```bash
   git clone https://github.com/your-repo/asl-interpreter.git
   cd asl-interpreter
   ```

2. **Set Up Backend**:  
   - Install dependencies:  
     ```bash
     pip install -r requirements.txt
     ```  
   - Run the Flask server:  
     ```bash
     python app.py
     ```

3. **Set Up Frontend**:  
   - Navigate to the frontend folder:  
     ```bash
     cd frontend
     npm install
     ```  
   - Run the Svelte app:  
     ```bash
     npm run dev
     ```

4. **Access the App**:  
   Open your browser and go to `http://localhost:5000`.

---

## References  
- [Ayush Thakur’s ASL Dataset](https://www.kaggle.com/datasets/ayuraj/asl-dataset).  
- [Akash Nagaraj’s ASL Alphabet Dataset](https://www.kaggle.com/datasets/grassknoted/asl-alphabet).
