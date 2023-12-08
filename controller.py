# controller.py
from model import AudioModel
from view import AudioView
import tkinter as tk
from tkinter import filedialog
from scipy.io import wavfile
import librosa
import numpy as np
import os  # Add this line to import the 'os' module
from pydub import AudioSegment

class AudioController:
    def __init__(self, root):
        self.model = AudioModel()
        self.view = AudioView(root, self)

    def load_audio(self):
        file_path = filedialog.askopenfilename(title="Select Audio File",
                                               filetypes=[("Audio files", "*.wav;*.mp3;*.aac")])

        if file_path:
            self.model.set_file_path(file_path)
            self.view.display_file_name(os.path.basename(file_path))

            sample_rate, audio_data = self.load_audio_file(file_path)
            self.model.set_audio_data(sample_rate, audio_data)
            self.view.display_waveform(audio_data, sample_rate)

            rt60_low, rt60_mid, rt60_high = self.calculate_rt60(audio_data, sample_rate)
            self.model.set_rt60_values(rt60_low, rt60_mid, rt60_high)

    def load_audio_file(self, file_path):
        if not file_path.lower().endswith('.wav'):
            audio = AudioSegment.from_file(file_path)
            y = np.array(audio.get_array_of_samples())
            return audio.frame_rate, y
        else:
            return wavfile.read(file_path)

    def load_wav(self, file_path):
        if not file_path.lower().endswith('.wav'):
            y, sr = librosa.load(file_path, sr=None)  # Load audio
            y = librosa.to_mono(y)  # Convert to mono if it's stereo
            y = librosa.util.normalize(y.astype(float))  # Ensure floating-point format
            return sr, y
        else:
            return wavfile.read(file_path)

    def calculate_rt60(self, audio_data, sample_rate):
        # Convert audio data to floating-point format
        audio_data_float = librosa.util.normalize(audio_data.astype(float))

        # Estimate autocorrelation function
        autocorr = librosa.autocorrelate(audio_data_float)

        # Define frequency bands for Low, Mid, and High
        low_freqs = (20 <= sample_rate / (np.arange(len(autocorr)) + np.finfo(float).eps)) & (sample_rate / (np.arange(len(autocorr)) + np.finfo(float).eps) < 250)
        mid_freqs = (250 <= sample_rate / (np.arange(len(autocorr)) + np.finfo(float).eps)) & (sample_rate / (np.arange(len(autocorr)) + np.finfo(float).eps) < 1000)
        high_freqs = (1000 <= sample_rate / (np.arange(len(autocorr)) + np.finfo(float).eps)) & (sample_rate / (np.arange(len(autocorr)) + np.finfo(float).eps) <= 5000)

        # Integrate autocorrelation within each frequency band
        rt60_low = self.compute_rt60(autocorr[low_freqs], sample_rate)
        rt60_mid = self.compute_rt60(autocorr[mid_freqs], sample_rate)
        rt60_high = self.compute_rt60(autocorr[high_freqs], sample_rate)

        return rt60_low, rt60_mid, rt60_high

    def compute_rt60(self, autocorr, sample_rate):
        # Compute power and sum along the appropriate axis
        power = np.abs(np.fft.fft(autocorr, axis=0))

        if power.ndim == 1:
            power_sum = np.sum(power)
            t_half = np.argmax(power > 0.5 * power_sum)
        else:
            power_sum = np.sum(power, axis=1)
            t_half = np.argmax(power_sum > 0.5 * power_sum[-1])

        # Calculate RT60 based on the time index
        rt60 = 2 * (power.shape[0] - t_half) / sample_rate

        return rt60

    def plot_rt60(self):
        rt60_low = self.model.rt60_low
        rt60_mid = self.model.rt60_mid
        rt60_high = self.model.rt60_high

        self.view.display_rt60_values(rt60_low, rt60_mid, rt60_high)

if __name__ == "__main__":
    root = tk.Tk()
    app = AudioController(root)
    root.mainloop()
