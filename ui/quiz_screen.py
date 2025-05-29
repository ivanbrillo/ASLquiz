import random
import time

import customtkinter as ctk

from config import FONT_FAMILY, ASL_CLASS_NAMES, errors
from utils.image_utils import load_asl_letter_image, process_frame


class QuizScreen(ctk.CTkFrame):

    def __init__(self, master):
        super().__init__(master)
        self.app = master
        self.target_letter = None
        self.test_mode = None  # video or image
        self.timer = 0
        self.number_attempts = 0
        self.video_completed = False  # flag to allow a 1-second delay between two words
        self._build_ui()

    def _build_ui(self):
        # Configure grid weights
        self.grid_columnconfigure((0, 1), weight=1)

        # Title
        self.label_title = ctk.CTkLabel(self, text="ASL Quiz", font=(FONT_FAMILY, 24, "bold"))
        self.label_title.grid(row=0, column=0, columnspan=2, pady=10)

        # Video canvas
        self.canvas = ctk.CTkCanvas(self, width=500, height=400, bg="black")
        self.canvas.grid(row=1, column=0, columnspan=2, pady=10)

        # Instruction
        self.label_instruction = ctk.CTkLabel(
            self, text="Show the sign for the letter below:", font=(FONT_FAMILY, 18)
        )
        self.label_instruction.grid(row=2, column=0, columnspan=2, pady=5)

        # Target letter frame
        self.letter_frame = ctk.CTkFrame(self)
        self.letter_frame.grid(row=3, column=0, columnspan=2, pady=10)
        self.letter_frame.grid_columnconfigure(0, weight=1)
        self.letter_frame.grid_columnconfigure(1, weight=1)

        # Target caption
        self.target_caption = ctk.CTkLabel(
            self.letter_frame,
            text="Current Letter:",
            font=(FONT_FAMILY, 16)
        )
        self.target_caption.grid(row=0, column=0, padx=20, pady=5)

        # Target letter display
        self.label_target = ctk.CTkLabel(
            self.letter_frame,
            text="",
            font=(FONT_FAMILY, 56, "bold"),
            text_color="#4F8DFD",
            width=150
        )
        self.label_target.grid(row=1, column=0, padx=20, pady=5)

        # ASL target image
        self.asl_image = ctk.CTkLabel(
            self.letter_frame,
            image=self.app.blank_ctk_image,
            text="",
            width=128,
            height=128
        )
        self.asl_image.grid(row=0, column=1, rowspan=2, padx=20, pady=10)

        # Prediction display
        self.prediction_frame = ctk.CTkFrame(self)
        self.prediction_frame.grid(row=4, column=0, columnspan=2, pady=10)
        self.prediction_frame.grid_columnconfigure(0, weight=1)
        self.prediction_frame.grid_columnconfigure(1, weight=1)

        # Prediction caption
        self.prediction_caption = ctk.CTkLabel(
            self.prediction_frame,
            text="Your Sign:",
            font=(FONT_FAMILY, 16)
        )
        self.prediction_caption.grid(row=0, column=0, padx=20, pady=5)

        # Predicted letter display
        self.predicted_letter = ctk.CTkLabel(
            self.prediction_frame,
            text="",
            font=(FONT_FAMILY, 56, "bold"),
            text_color="#FFB347",
            width=150
        )
        self.predicted_letter.grid(row=1, column=0, padx=20, pady=5)

        # ASL predicted image
        self.predicted_image = ctk.CTkLabel(
            self.prediction_frame,
            image=self.app.blank_ctk_image,
            text="",
            width=128,
            height=128
        )
        self.predicted_image.grid(row=0, column=1, rowspan=2, padx=20, pady=10)

        # Text input (for image mode)
        self.text_input_frame = ctk.CTkFrame(self)
        self.text_input_frame.grid(row=5, column=0, columnspan=2, pady=10)

        self.entry_input = ctk.CTkEntry(
            self.text_input_frame,
            width=200,
            font=(FONT_FAMILY, 16),
            placeholder_text="Enter letter"
        )
        self.entry_input.grid(row=0, column=0, padx=10, pady=10)

        self.button_submit = ctk.CTkButton(
            self.text_input_frame,
            text="Submit",
            font=(FONT_FAMILY, 16),
            command=self._on_submit
        )
        self.button_submit.grid(row=0, column=1, padx=10, pady=10)

        # Feedback
        self.label_feedback = ctk.CTkLabel(
            self, text="", font=(FONT_FAMILY, 24, "bold")
        )
        self.label_feedback.grid(row=6, column=0, columnspan=2, pady=10)

        # Controls
        self.button_next = ctk.CTkButton(
            self, text="Next Letter", font=(FONT_FAMILY, 16), command=self.app.next_letter
        )
        self.button_next.grid(row=7, column=0, pady=(0, 30), sticky="e", padx=(0, 10))

        self.button_home = ctk.CTkButton(
            self, text="Back to Home", font=(FONT_FAMILY, 16), command=self.app.show_home_screen
        )
        self.button_home.grid(row=7, column=1, pady=(0, 30), sticky="w", padx=(10, 0))

    def video_text_selector(self, epsilon=0.3):
        if random.random() < epsilon:
            return random.choice(['video', 'text'])

        Ev = errors['video_total_errors']
        Nv = errors['video_tests']
        Et = errors['text_total_errors']
        Nt = errors['text_tests']

        # avoid div/0
        if Nv == 0: return 'video'
        if Nt == 0: return 'text'

        rv = Ev / Nv
        rt = Et / Nt

        bal_v = (Nt / Nv) ** 0.5
        bal_t = (Nv / Nt) ** 0.5

        score_v = rv * bal_v
        score_t = rt * bal_t

        p_video = score_v / (score_v + score_t)
        return 'video' if random.random() < p_video else 'text'

    def select_next_letter(self, t="text", epsilon=0.3):
        # 1) with small chance, pick any letter at random
        if random.random() < epsilon:
            return random.choice(ASL_CLASS_NAMES)

        # 2) build weights = text_errors
        weights = []
        for ltr in ASL_CLASS_NAMES:
            te = errors['letters'][ltr][t + '_errors']
            weights.append(te)

        # 3) randomly choose a letter weighted by its errors
        return random.choices(ASL_CLASS_NAMES, weights=weights, k=1)[0]

    def next_letter(self, difficulty):
        # Update errors if needed
        if self.timer != 0:
            self.update_video_error()
        if self.number_attempts != 0:
            self.update_text_error()

        # Reset video_completed flag for new letter
        self.video_completed = False

        # Hide all optional UI elements
        self.prediction_frame.grid_remove()
        self.text_input_frame.grid_remove()
        self.label_feedback.configure(text="")

        # Reset displays
        self.label_target.configure(text="")
        self.predicted_letter.configure(text="")
        self.asl_image.configure(image=self.app.blank_ctk_image, text="")
        self.predicted_image.configure(image=self.app.blank_ctk_image, text="")

        # Pick mode and letter
        self.test_mode = self.video_text_selector()
        self.target_letter = self.select_next_letter(self.test_mode)

        if self.test_mode == 'video':
            self.timer = time.time()
            # Show camera & prompt
            self.canvas.grid()
            self.label_instruction.configure(text="Show the sign for the letter below:")
            self.label_target.configure(text=self.target_letter)

            if difficulty == 'easy':
                # Show target image in easy mode
                img_t = load_asl_letter_image(self.target_letter)
                self.asl_image.configure(
                    image=img_t or self.app.blank_ctk_image,
                    text="" if img_t else "Image not found"
                )
                # Show prediction frame for easy mode
                self.prediction_frame.grid()
            else:
                # Hard mode - explicitly hide the image area
                self.asl_image.grid_remove()
                # Center the target letter in the frame (since image is hidden)
                self.letter_frame.grid_columnconfigure(1, weight=0)  # Remove weight from image column
        else:
            # Static image test mode
            self.number_attempts = 0
            self.canvas.grid_remove()
            self.label_instruction.configure(text="Identify the letter shown in the image:")

            # Show image and input controls
            img = load_asl_letter_image(self.target_letter)
            self.asl_image.grid()  # Make sure image is visible for text mode
            self.letter_frame.grid_columnconfigure(1, weight=1)  # Restore image column weight
            self.asl_image.configure(
                image=img or self.app.blank_ctk_image,
                text="" if img else "Image not found"
            )

            # Show text input controls
            self.text_input_frame.grid()
            self.entry_input.delete(0, ctk.END)
            self.entry_input.focus_set()

        self.app._adjust_window_size()

    def update_prediction(self, predicted_letter):
        # Process predictions only in video mode
        if self.test_mode == 'video':
            if self.video_completed:
                return  # Ignore further predictions until next letter

            # Always update the predicted letter text
            self.predicted_letter.configure(text=predicted_letter)

            if predicted_letter == self.target_letter:
                self.label_feedback.configure(text="Correct!", text_color="green")
                self.update_video_error(correct=True)
                self.video_completed = True  # Mark as completed
                self.after(1000, self.app.next_letter)
            else:
                self.label_feedback.configure(text=f"Keep trying!", text_color="orange")

            # Show predicted image only in easy mode
            if self.app.difficulty == 'easy':
                img_p = load_asl_letter_image(predicted_letter)
                self.predicted_image.configure(
                    image=img_p or self.app.blank_ctk_image,
                    text=""
                )

    def clear_prediction(self):
        if self.test_mode == 'video':
            # Clear prediction display
            self.predicted_letter.configure(text="")
            self.predicted_image.configure(image=self.app.blank_ctk_image, text="")
            self.label_feedback.configure(text="No hand detected", text_color="orange")

    def update_canvas(self, frame):
        if self.test_mode == 'video':
            imgtk = process_frame(frame)
            self.canvas.create_image(0, 0, anchor="nw", image=imgtk)
            self.canvas.imgtk = imgtk

    def _on_submit(self):
        user_input = self.entry_input.get().strip().upper()
        if not user_input:
            return

        if user_input == self.target_letter:
            self.label_feedback.configure(text="Correct!", text_color="green")
            self.update_text_error(correct=True)
            self.after(500, self.app.next_letter)
        else:
            self.number_attempts = self.number_attempts + 1
            self.label_feedback.configure(text=f"Incorrect. Try again.", text_color="red")

        self.entry_input.delete(0, ctk.END)

    def update_text_error(self, correct=False):
        add = 1 if not correct else self.number_attempts / (self.number_attempts + 1)
        errors['text_total_errors'] += add
        errors['text_tests'] += 1
        errors['letters'][self.target_letter]['text_errors'] += add
        self.number_attempts = 0
        print(errors)

    def update_video_error(self, correct=False):
        used_time = time.time() - self.timer
        used_time = min(0 if used_time < 2 else used_time / 10, 1)
        add = 1 if not correct else used_time

        errors['video_total_errors'] += add
        errors['video_tests'] += 1
        errors['letters'][self.target_letter]['video_errors'] += add
        self.timer = 0
        print(errors)
