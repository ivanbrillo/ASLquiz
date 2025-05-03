import mediapipe as mp
import numpy as np
import tensorflow as tf

from config import MODEL_PATH, ASL_CLASS_NAMES, MEDIAPIPE_HANDS_CONFIG


class HandDetector:

    def __init__(self):
        # Initialize MediaPipe hands
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(**MEDIAPIPE_HANDS_CONFIG)

        # Load the trained model
        self.model = tf.keras.models.load_model(MODEL_PATH)
        self.class_names = ASL_CLASS_NAMES

    def process_frame(self, frame):
        """
        Args:
            frame (numpy.ndarray): The input frame

        Returns:
            tuple: (processed_frame, results) where results is the MediaPipe detection results
        """
        results = self.hands.process(frame)

        # Filter out left hands and keep only the right hand
        if results.multi_handedness and results.multi_hand_landmarks:
            right_hand_index = None
            for i, handedness in enumerate(results.multi_handedness):
                if handedness.classification[0].label == "Right":
                    right_hand_index = i
                    break

            if right_hand_index is not None:
                # Keep only the right hand landmarks
                results.multi_hand_landmarks = [results.multi_hand_landmarks[right_hand_index]]
                results.multi_handedness = [results.multi_handedness[right_hand_index]]
            else:
                # No right hand detected
                results.multi_hand_landmarks = None
                results.multi_handedness = None

        # Draw landmarks on the frame if the right hand is detected
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS
                )

        return frame, results

    def extract_landmarks(self, results):
        """
        Args:
            results: MediaPipe hand detection results

        Returns:
            numpy.ndarray or None: Extracted landmarks array or None if no right hands detected
        """
        if not results.multi_hand_landmarks:
            return None

        landmarks = []
        for hand_landmarks in results.multi_hand_landmarks[:1]:  # Using only the first right hand
            for landmark in hand_landmarks.landmark:
                landmarks.extend([landmark.x, landmark.y, landmark.z])

        return np.array([landmarks]) if len(landmarks) == 63 else None

    def predict_letter(self, landmarks):
        """
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
        self.hands.close()
