import tkinter as tk
from tkinter import filedialog
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.io import wavfile
import librosa
import librosa.display

class AudioAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Analyzer")

        self.load_button = tk.Button(root, text="Load Audio File", command=self.load_audio)
        self.load_button.pack(pady=10)

        self.result_label = tk.Label(root, text="")
        self.result_label.pack()

    def load_audio(self):
        file_path = filedialog.askopenfilename(title="Select Audio File", filetypes=[("Audio files", "*.wav;*.mp3;*.aac")])

        if file_path:
            self.process_audio(file_path)

    def process_audio(self, file_path):
        self.result_label.config(text="Processing...")

        # Check if the file is WAV, if not, convert it
        if not file_path.lower().endswith('.wav'):
            converted_path = self.convert_to_wav(file_path)
            if converted_path:
                file_path = converted_path
            else:
                return

        # Display file name
        self.result_label.config(text=f"File: {os.path.basename(file_path)}")

        # Load WAV file
        sample_rate, audio_data = wavfile.read(file_path)

        # Check for meta data (tags) and remove if present
        if 'INFO' in audio_data:
            audio_data = audio_data['INFO']

        # Check for multi-channel and convert to one channel
        if len(audio_data.shape) > 1:
            audio_data = audio_data[:, 0]

        # Display time value of .wav in seconds
        duration = len(audio_data) / sample_rate
        print(f"Duration of audio: {duration} seconds")

        # Display waveform of .wav
        plt.figure(figsize=(10, 4))
        librosa.display.waveshow(audio_data, sr=sample_rate)
        plt.title('Waveform')
        plt.show()

        # Data Analysis and Modeling (example using NumPy and SciPy)
        rt60_low, rt60_mid, rt60_high = self.calculate_rt60(audio_data, sample_rate)

        print(f"RT60 Low: {rt60_low} seconds")
        print(f"RT60 Mid: {rt60_mid} seconds")
        print(f"RT60 High: {rt60_high} seconds")

        # Visualize RT60 data for each frequency range
        self.plot_rt60(rt60_low, rt60_mid, rt60_high)

    def convert_to_wav(self, file_path):
        try:
            y, sr = librosa.load(file_path, sr=None)
            new_path = file_path.rsplit('.', 1)[0] + '.wav'
            wavfile.write(new_path, sr, y)
            return new_path
        except Exception as e:
            print(f"Error converting to WAV: {e}")
            return None

    def calculate_rt60(self, audio_data, sample_rate):
        # Calculate RT60 for Low, Mid, and High frequencies using LibROSA
        # You may need to adjust this based on your specific requirements

        # Compute Short-Time Fourier Transform (STFT)
        stft = librosa.stft(audio_data)

        # Calculate power spectrogram
        power_spec = np.abs(stft) ** 2

        # Define frequency bands (Low, Mid, High)
        freq_bins = librosa.fft_frequencies(sr=sample_rate)
        low_freqs = (freq_bins >= 20) & (freq_bins < 500)
        mid_freqs = (freq_bins >= 500) & (freq_bins < 2000)
        high_freqs = (freq_bins >= 2000) & (freq_bins <= 8000)

        # Integrate power within each frequency band
        power_low = np.sum(power_spec[low_freqs, :])
        power_mid = np.sum(power_spec[mid_freqs, :])
        power_high = np.sum(power_spec[high_freqs, :])

        # Calculate RT60 for each frequency band
        rt60_low = self.compute_rt60(power_low, sample_rate)
        rt60_mid = self.compute_rt60(power_mid, sample_rate)
        rt60_high = self.compute_rt60(power_high, sample_rate)

        return rt60_low, rt60_mid, rt60_high

    def compute_rt60(self, power, sample_rate):
        # Compute RT60 from power spectrogram
        # You may need to adjust this based on your specific requirements

        # Sum the power over time
        power_sum = np.sum(power, axis=1)

        # Find the time point where the power drops to half
        half_power = 0.5 * power_sum[-1]
        t_half = np.argmax(power_sum > half_power)

        # Calculate RT60 in seconds
        rt60 = 2 * (len(power_sum) - t_half) / sample_rate

        return rt60

    def plot_rt60(self, rt60_low, rt60_mid, rt60_high):
        # Plot RT60 for Low, Mid, and High frequencies
        frequencies = ['Low', 'Mid', 'High']
        rt60_values = [rt60_low, rt60_mid, rt60_high]

        plt.bar(frequencies, rt60_values, color=['blue', 'green', 'red'])
        plt.title('RT60 for Low, Mid, High Frequencies')
        plt.xlabel('Frequency Range')
        plt.ylabel('RT60 (seconds)')
        plt.show()


if __name__ == "__main__":
    root = tk.Tk()
    app = AudioAnalyzer(root)
    root.mainloop()
