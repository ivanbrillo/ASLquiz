"""
Main application class for the ASL Quiz
"""
import customtkinter as ctk
import cv2
from config import WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE, CAMERA_INDEX
from ui.home_screen import HomeScreen
from ui.quiz_screen import QuizScreen
from models.hand_detector import HandDetector
from utils.image_utils import create_blank_image, create_ctk_image


class ASLQuizApp(ctk.CTk):
    """Main ASL Quiz Application class"""

    def __init__(self):
        """Initialize the application"""
        super().__init__()

        # Set up the main window
        self.title(WINDOW_TITLE)
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

        # Initialize variables
        self.cap = None
        self.detector = None
        self.difficulty = "easy"
        self.target_letter = None

        # Create blank image for placeholders
        blank_image = create_blank_image()
        self.blank_ctk_image = create_ctk_image(blank_image)

        # Create frames for screens
        self.home_screen = HomeScreen(self)
        self.quiz_screen = QuizScreen(self)

        # Set up initial screen
        self.show_home_screen()

    def show_home_screen(self):
        """Show the home screen and hide other screens"""
        self.quiz_screen.pack_forget()
        self.home_screen.pack(fill="both", expand=True)

        # Release camera and detector if active
        self._release_resources()

    def start_quiz(self, difficulty):
        """
        Start the quiz with the selected difficulty

        Args:
            difficulty (str): Difficulty level ("easy" or "hard")
        """
        self.difficulty = difficulty
        self.home_screen.pack_forget()
        self.quiz_screen.pack(fill="both", expand=True)

        # Initialize camera and hand detector
        self.cap = cv2.VideoCapture(CAMERA_INDEX)
        if not self.cap.isOpened():
            raise RuntimeError("Could not open webcam")

        self.detector = HandDetector()

        # Generate the first letter and start processing frames
        self.next_letter()
        self.update_frame()

    def next_letter(self):
        """Generate the next letter for the quiz"""
        # Let the quiz screen handle the letter selection and display
        self.quiz_screen.next_letter(self.difficulty)

    def update_frame(self):
        """Update the webcam feed and process hand gestures"""
        if not self.cap or not self.detector:
            return

        # Capture frame
        success, frame = self.cap.read()
        if not success:
            self.after(10, self.update_frame)
            return

        # Flip frame for mirror effect and process with hand detector
        frame = cv2.flip(frame, 1)
        processed_frame, results = self.detector.process_frame(frame)

        # Process hand detection results
        landmarks = self.detector.extract_landmarks(results)
        if landmarks is not None:
            # Get prediction
            predicted_letter, confidence = self.detector.predict_letter(landmarks)
            if predicted_letter:
                self.quiz_screen.update_prediction(predicted_letter)
        else:
            # Clear prediction when no hand detected
            self.quiz_screen.clear_prediction()

        # Update the canvas with the processed frame
        self.quiz_screen.update_canvas(processed_frame)

        # Schedule next frame update
        self.after(10, self.update_frame)

    def on_closing(self):
        """Handle application closing"""
        self._release_resources()
        self.destroy()

    def _release_resources(self):
        """Release camera and other resources"""
        if self.cap:
            self.cap.release()
            self.cap = None

        if self.detector:
            self.detector.close()
            self.detector = None