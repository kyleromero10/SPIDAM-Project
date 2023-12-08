# view.py
import tkinter as tk
from tkinter import filedialog
import os
import matplotlib.pyplot as plt
import librosa.display

class AudioView:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller

        self.load_button = tk.Button(root, text="Load Audio File", command=self.controller.load_audio)
        self.load_button.pack(pady=10)

        self.result_label = tk.Label(root, text="")
        self.result_label.pack()

        self.plot_button = tk.Button(root, text="Plot RT60", command=self.controller.plot_rt60)
        self.plot_button.pack(pady=10)

    def display_file_name(self, file_name):
        self.result_label.config(text=f"File: {file_name}")

    def display_waveform(self, audio_data, sample_rate):
        plt.figure(figsize=(10, 4))
        librosa.display.waveshow(audio_data, sr=sample_rate)
        plt.title('Waveform')
        plt.show()

    def display_rt60_values(self, rt60_low, rt60_mid, rt60_high):
        frequencies = ['Low', 'Mid', 'High']
        rt60_values = [rt60_low, rt60_mid, rt60_high]

        plt.bar(frequencies, rt60_values, color=['blue', 'green', 'red'])
        plt.title('RT60 for Low, Mid, High Frequencies')
        plt.xlabel('Frequency Range')
        plt.ylabel('RT60 (seconds)')
        plt.show()
