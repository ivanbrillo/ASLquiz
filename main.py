import os

# Disable TensorFlow warnings
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import customtkinter as ctk
from ui.app import ASLQuizApp

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    app = ASLQuizApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
