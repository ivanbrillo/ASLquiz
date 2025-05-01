#!/usr/bin/env python3
"""
ASL Quiz Application - Main Entry Point
"""
import os

# Disable oneDNN custom operations warnings before any imports
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import customtkinter as ctk
from ui.app import ASLQuizApp

if __name__ == "__main__":
    # Set appearance mode
    ctk.set_appearance_mode("dark")

    # Initialize and run the application
    app = ASLQuizApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()