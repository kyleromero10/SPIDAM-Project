# controller.py
from model import AudioModel
from view import AudioView
import tkinter as tk
from tkinter import filedialog
from scipy.io import wavfile
import librosa
import numpy as np

class AudioController:
    def __init__(self, root):
        self.model = AudioModel()
        self.view = AudioView(root, self)

    def load_audio(self):
        file_path = filedialog.askopenfilename(title="Select Audio File", filetypes=[("Audio files", "*.wav;*.mp3;*.aac")])

        if file_path:
            self.model.set_file_path(file_path)
            self.view.display_file_name(os.path.basename(file_path))

            sample_rate, audio_data = self.load_wav(file_path)
            self.model.set_audio_data(sample_rate, audio_data)
            self.view.display_waveform(audio_data, sample_rate)

            rt60_low, rt60_mid, rt60_high = self.calculate_rt60(audio_data, sample_rate)
            self.model.set_rt60_values(rt60_low, rt60_mid, rt60_high)

    def load_wav(self, file_path):
        if not file_path.lower().endswith('.wav'):
            y, sr = librosa.load(file_path, sr=None)
            return sr, y
        else:
            return wavfile.read(file_path)

    def calculate_rt60(self, audio_data, sample_rate):
        # Calculate RT60 for Low, Mid, and High frequencies using LibROSA
        stft = librosa.stft(audio_data)
        power_spec = np.abs(stft) ** 2

        freq_bins = librosa.fft_frequencies(sr=sample_rate)
        low_freqs = (freq_bins >= 20) & (freq_bins < 500)
        mid_freqs = (freq_bins >= 500) & (freq_bins < 2000)
        high_freqs = (freq_bins >= 2000) & (freq_bins <= 8000)

        power_low = np.sum(power_spec[low_freqs, :])
        power_mid = np.sum(power_spec[mid_freqs, :])
        power_high = np.sum(power_spec[high_freqs, :])

        rt60_low = self.compute_rt60(power_low, sample_rate)
        rt60_mid = self.compute_rt60(power_mid, sample_rate)
        rt60_high = self.compute_rt60(power_high, sample_rate)

        return rt60_low, rt60_mid, rt60_high

    def compute_rt60(self, power, sample_rate):
        power_sum = np.sum(power, axis=1)
        half_power = 0.5 * power_sum[-1]
        t_half = np.argmax(power_sum > half_power)
        rt60 = 2 * (len(power_sum) - t_half) / sample_rate
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
