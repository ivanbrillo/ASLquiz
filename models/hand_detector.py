"""
HandDetector class handles MediaPipe hand tracking and ASL sign recognition
"""
import numpy as np
import tensorflow as tf
import mediapipe as mp
import cv2
from config import MODEL_PATH, ASL_CLASS_NAMES, MEDIAPIPE_HANDS_CONFIG


class HandDetector:
    """Hand detection and ASL sign prediction class"""

    def __init__(self):
        """Initialize MediaPipe hands module and load the TensorFlow model"""
        # Initialize MediaPipe hands
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(**MEDIAPIPE_HANDS_CONFIG)

        # Load the trained model
        self.model = tf.keras.models.load_model(MODEL_PATH)
        self.class_names = ASL_CLASS_NAMES

    def process_frame(self, frame):
        """
        Process a video frame and detect hands

        Args:
            frame (numpy.ndarray): The input frame

        Returns:
            tuple: (processed_frame, results) where results is the MediaPipe detection results
        """
        # Convert the frame to RGB for MediaPipe
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(image_rgb)

        # Draw landmarks on the frame if hands are detected
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

        return frame, results

    def extract_landmarks(self, results):
        """
        Extract hand landmarks from MediaPipe results

        Args:
            results: MediaPipe hand detection results

        Returns:
            numpy.ndarray or None: Extracted landmarks array or None if no hands detected
        """
        if not results.multi_hand_landmarks:
            return None

        landmarks = []
        for hand_landmarks in results.multi_hand_landmarks[:1]:  # Using only the first hand
            for landmark in hand_landmarks.landmark:
                landmarks.extend([landmark.x, landmark.y, landmark.z])

        return np.array([landmarks]) if len(landmarks) == 63 else None

    def predict_letter(self, landmarks):
        """
        Predict ASL letter from hand landmarks

        Args:
            landmarks (numpy.ndarray): Hand landmarks array

        Returns:
            str: Predicted letter
            float: Confidence score
        """
        if landmarks is None:
            return None, 0.0

        prediction = self.model.predict(landmarks, verbose=0)[0]
        predicted_class_idx = np.argmax(prediction)
        confidence = prediction[predicted_class_idx]

        return self.class_names[predicted_class_idx], confidence

    def close(self):
        """Release resources"""
        self.hands.close()