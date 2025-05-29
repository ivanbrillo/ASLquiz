import customtkinter as ctk
import cv2

from config import FONT_FAMILY, ASL_CLASS_NAMES
from utils.image_utils import load_asl_letter_image, process_frame


class PhraseScreen(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.app = master
        self.phrase = ""
        self.current_index = 0
        self.timer = 0
        self.phrase_errors = 0
        self.letter_completed = False
        self._build_ui()

    def _build_ui(self):
        # Configure grid weights
        self.grid_columnconfigure((0, 1), weight=1)

        # Title
        self.label_title = ctk.CTkLabel(self, text="ASL Phrase Practice", font=(FONT_FAMILY, 24, "bold"))
        self.label_title.grid(row=0, column=0, columnspan=2, pady=10)

        # Full phrase display
        self.phrase_frame = ctk.CTkFrame(self)
        self.phrase_frame.grid(row=1, column=0, columnspan=2, pady=10, padx=20, sticky="ew")
        self.phrase_frame.grid_columnconfigure(0, weight=1)

        self.phrase_label = ctk.CTkLabel(
            self.phrase_frame,
            text="",
            font=(FONT_FAMILY, 24),
            anchor="center"
        )
        self.phrase_label.grid(row=0, column=0, sticky="ew", pady=10, padx=10)

        # Progress label
        self.progress_label = ctk.CTkLabel(
            self,
            text="Progress: 0/0",
            font=(FONT_FAMILY, 14)
        )
        self.progress_label.grid(row=2, column=0, columnspan=2, pady=5)

        # Video canvas
        self.canvas = ctk.CTkCanvas(self, width=500, height=400, bg="black")
        self.canvas.grid(row=3, column=0, columnspan=2, pady=10)

        # Current target letter display
        self.letter_frame = ctk.CTkFrame(self)
        self.letter_frame.grid(row=4, column=0, columnspan=2, pady=10)

        # Current target caption
        self.target_caption = ctk.CTkLabel(
            self.letter_frame,
            text="Current Letter:",
            font=(FONT_FAMILY, 16)
        )
        self.target_caption.grid(row=0, column=0, padx=20, pady=5)

        # Current letter
        self.current_letter = ctk.CTkLabel(
            self.letter_frame,
            text="",
            font=(FONT_FAMILY, 56, "bold"),
            text_color="#4F8DFD"
        )
        self.current_letter.grid(row=1, column=0, padx=20, pady=5)

        # ASL image reference
        self.asl_image = ctk.CTkLabel(
            self.letter_frame,
            image=self.app.blank_ctk_image,
            text=""
        )
        self.asl_image.grid(row=0, column=1, rowspan=2, padx=20, pady=10)

        # Feedback
        self.label_feedback = ctk.CTkLabel(
            self, text="", font=(FONT_FAMILY, 24, "bold")
        )
        self.label_feedback.grid(row=5, column=0, columnspan=2, pady=10)

        # Controls
        self.button_skip = ctk.CTkButton(
            self, text="Skip Letter", font=(FONT_FAMILY, 16), command=self._skip_letter
        )
        self.button_skip.grid(row=6, column=0, pady=(0, 10), sticky="e", padx=(0, 10))

        self.button_new = ctk.CTkButton(
            self, text="New Phrase", font=(FONT_FAMILY, 16), command=self._new_phrase
        )
        self.button_new.grid(row=6, column=1, pady=(0, 10), sticky="w", padx=(10, 0))

        self.button_home = ctk.CTkButton(
            self, text="Back to Home", font=(FONT_FAMILY, 16), command=self.app.show_home_screen
        )
        self.button_home.grid(row=7, column=0, columnspan=2, pady=(0, 30))

    def start_phrase_practice(self, phrase=None):
        """Initialize or reset the phrase practice with a new or provided phrase"""
        if not phrase:
            # Default phrases list
            phrases = [
                "HELLO WORLD",
                "LEARN ASL",
                "SIGN LANGUAGE",
                "PRACTICE MAKES PERFECT",
                "GOOD MORNING",
                "NICE TO MEET YOU"
            ]
            import random
            phrase = random.choice(phrases)

        # Convert to uppercase and filter out characters not in ASL_CLASS_NAMES
        self.phrase = "".join([c for c in phrase.upper() if c in ASL_CLASS_NAMES or c == " "])
        self.current_index = 0
        self.phrase_errors = 0
        self.letter_completed = False

        # Initialize display for the first letter
        self._update_phrase_display()

        # Begin camera processing if not already running
        if not self.app.cap or not self.app.detector:
            self.app.cap = self.app._init_camera()
            self.app.detector = self.app._init_detector()

        # Start processing frames
        self.update_frame()

    def _update_phrase_display(self):
        """Update the phrase display"""
        if not self.phrase:
            return

        # Just display the phrase as plain text, no caret marker
        self.phrase_label.configure(
            text=self.phrase,
            font=(FONT_FAMILY, 24)
        )

        # Update progress
        self.progress_label.configure(
            text=f"Progress: {min(self.current_index, len(self.phrase))}/{len(self.phrase)} letters"
        )

        # Update current letter display and image
        if self.current_index < len(self.phrase) and self.phrase[self.current_index] != " ":
            current_letter = self.phrase[self.current_index]
            self.current_letter.configure(text=current_letter)

            # Load and display the ASL image for the current letter
            img = load_asl_letter_image(current_letter)
            if img:
                self.asl_image.configure(image=img, text="")
            else:
                self.asl_image.configure(image=self.app.blank_ctk_image, text="Image not found")
        elif self.current_index < len(self.phrase) and self.phrase[self.current_index] == " ":
            # Handle space
            self.current_letter.configure(text="SPACE")
            self.asl_image.configure(image=self.app.blank_ctk_image, text="")
            # Auto-advance past spaces after a short delay
            self.after(1000, lambda: self._move_to_next_letter(auto_advance=True))
        else:
            # End of phrase
            self.current_letter.configure(text="")
            self.asl_image.configure(image=self.app.blank_ctk_image, text="")

    def update_frame(self):
        """Update the webcam feed and process hand gestures"""
        if not self.app.cap or not self.app.detector:
            return

        # Capture frame
        success, frame = self.app.cap.read()
        if not success:
            self.after(10, self.update_frame)
            return

        # Flip frame for mirror effect and process with hand detector
        frame = cv2.flip(frame, 1)
        processed_frame, results = self.app.detector.process_frame(frame)

        # Process hand detection results
        if self.current_index < len(self.phrase) and self.phrase[self.current_index] != " ":
            landmarks = self.app.detector.extract_landmarks(results)
            if landmarks is not None:
                # Get prediction
                predicted_letter, confidence = self.app.detector.predict_letter(landmarks)
                if predicted_letter:
                    self._handle_prediction(predicted_letter)
            else:
                # No hand detected
                self.label_feedback.configure(text="No hand detected", text_color="orange")

        # Update the canvas with the processed frame
        imgtk = process_frame(processed_frame)
        self.canvas.create_image(0, 0, anchor="nw", image=imgtk)
        self.canvas.imgtk = imgtk

        # Schedule next frame update if we're still in the phrase
        if self.current_index < len(self.phrase):
            self.after(10, self.update_frame)
        else:
            # Phrase completed!
            self._show_completion()

    def _handle_prediction(self, predicted_letter):
        """Handle a letter prediction from the hand detector"""
        if self.letter_completed:
            return  # Ignore predictions during the pause between letters

        target_letter = self.phrase[self.current_index]

        if predicted_letter == target_letter:
            # Correct letter!
            self.label_feedback.configure(text="Correct!", text_color="green")
            self.letter_completed = True

            # Add a slight delay before moving to next letter
            self.after(1000, lambda: self._move_to_next_letter())
        else:
            # Wrong letter
            self.label_feedback.configure(
                text=f"Showing: {predicted_letter}",
                text_color="red"
            )
            self.phrase_errors += 1

    def _move_to_next_letter(self, auto_advance=False):
        """Advance to the next letter in the phrase"""
        # Reset completion flag
        self.letter_completed = False

        # Advance index
        self.current_index += 1

        # Update display
        self._update_phrase_display()

        # Clear feedback
        if not auto_advance:
            self.label_feedback.configure(text="")

        # Check if we've completed the phrase
        if self.current_index >= len(self.phrase):
            self._show_completion()

    def _show_completion(self):
        """Show phrase completion feedback"""
        # Display completion message
        self.label_feedback.configure(
            text="Phrase Completed!",
            text_color="green"
        )

    def _skip_letter(self):
        """Skip the current letter"""
        if self.current_index < len(self.phrase):
            self.phrase_errors += 1
            self._move_to_next_letter()

    def _new_phrase(self):
        """Start a new random phrase"""
        self.start_phrase_practice()

    def on_closing(self):
        """Handle screen closing"""
        # Stop camera processing
        if self.app.cap:
            self.app.cap.release()
            self.app.cap = None

        if self.app.detector:
            self.app.detector.close()
            self.app.detector = None
