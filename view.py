# view.py
import tkinter as tk
from tkinter import filedialog
import os
import matplotlib.pyplot as plt
import librosa.util

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
        # Convert audio_data to floating-point format
        audio_data_float = librosa.util.normalize(audio_data.astype(float))

        plt.figure(figsize=(10, 4))
        plt.plot(audio_data_float)
        plt.title('Waveform')
        plt.show()

    def display_rt60_values(self, rt60_low, rt60_mid, rt60_high):
        frequencies = ['Low', 'Mid', 'High']

        # Check if any of the values is None and replace it with a default value (0 in this case)
        rt60_low = rt60_low if rt60_low is not None else 0
        rt60_mid = rt60_mid if rt60_mid is not None else 0
        rt60_high = rt60_high if rt60_high is not None else 0

        plt.bar(frequencies, [rt60_low, rt60_mid, rt60_high], color=['blue', 'green', 'red'])
        plt.title('RT60 for Low, Mid, High Frequencies')
        plt.xlabel('Frequency Range')
        plt.ylabel('RT60 (seconds)')
        plt.show()
