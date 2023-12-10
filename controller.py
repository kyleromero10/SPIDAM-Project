# controller.py
from model import AudioModel
from view import AudioView
import tkinter as tk
from tkinter import filedialog
from scipy.io import wavfile
import librosa
import numpy as np
import os
import subprocess
import matplotlib.pyplot as plt
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
            ffmpeg_path = os.path.join(os.path.dirname(__file__), 'ffmpeg.exe')
            output_path = os.path.join(os.path.dirname(file_path), 'output.wav')

            # Use ffmpeg to convert the input file to WAV and remove metadata
            command = [ffmpeg_path, '-i', file_path, '-acodec', 'pcm_s16le', '-ar', '44100', '-ac', '1', output_path]
            subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            # Load the processed WAV file
            audio = AudioSegment.from_file(output_path)
            channels = audio.channels
            if channels > 1:
                # Convert to mono (single channel) if there are multiple channels
                audio = audio.set_channels(1)
            audio_data = np.array(audio.get_array_of_samples())

            # Remove the temporary output file
            os.remove(output_path)

            return audio.frame_rate, audio_data
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
        # Compute autocorrelation
        autocorr = np.correlate(audio_data, audio_data, mode='full')

        # Get frequency bands
        low_freqs, mid_freqs, high_freqs = self.get_frequency_ranges(sample_rate)

        # Compute RT60 for each frequency range
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
            rt60 = 2 * (len(autocorr) - t_half) / sample_rate
        else:
            power_sum = np.sum(power, axis=1)
            t_half = np.argmax(power_sum > 0.5 * power_sum[-1])
            rt60 = 2 * (len(autocorr) - t_half) / sample_rate

        rt60_array = 2 * (len(autocorr) - np.arange(len(autocorr))) / sample_rate

        return rt60_array

    def get_frequency_ranges(self, sample_rate):
        low_freqs = np.arange(0, 1000)  # Adjust the upper limit as needed
        mid_freqs = np.arange(1000, 5000)  # Adjust the upper limit as needed
        high_freqs = np.arange(5000, sample_rate / 2)  # Adjust the lower and upper limits as needed

        # Convert high_freqs to integers
        high_freqs = high_freqs.astype(int)

        return low_freqs, mid_freqs, high_freqs

    def plot_rt60(self):
        rt60_low = np.atleast_1d(self.model.rt60_low)
        rt60_mid = np.atleast_1d(self.model.rt60_mid)
        rt60_high = np.atleast_1d(self.model.rt60_high)



        min_len = min(rt60_low.size, rt60_mid.size, rt60_high.size)

        rt60_low = rt60_low[:min_len]
        rt60_mid = rt60_mid[:min_len]
        rt60_high = rt60_high[:min_len]

        self.model.set_rt60_values(rt60_low, rt60_mid, rt60_high)

        self.view.display_rt60_values(np.array(rt60_low), np.array(rt60_mid), np.array(rt60_high),
                                      self.merge_rt60_values, self.unmerge_rt60_values)

    def merge_rt60_values(self, rt60_low, rt60_mid, rt60_high):
        # Create a new figure for the merged graph
        plt.figure(figsize=(10, 4))

        # Plot the merged graph
        plt.plot(rt60_low, label='Low Frequency', color='blue')
        plt.plot(rt60_mid, label='Mid Frequency', color='green')
        plt.plot(rt60_high, label='High Frequency', color='red')

        plt.title('Merged RT60 for Low, Mid, High Frequencies')
        plt.xlabel('Time (seconds)')
        plt.ylabel('Power (dB)')
        plt.legend()

        # Calculate the RT60 difference
        avg_rt60 = np.mean([np.mean(rt60_low), np.mean(rt60_mid), np.mean(rt60_high)])
        rt60_difference = avg_rt60 - 0.5

        plt.text(0.5, 0.1, f'RT60 Difference: {rt60_difference:.2f} seconds', transform=plt.gca().transAxes,
                 color='black', fontsize=12, fontweight='bold', ha='center')

        plt.show()

    def compute_highest_resonance(self, audio_data, sample_rate):
        # Compute the FFT
        fft_result = np.fft.fft(audio_data)

        frequencies = np.fft.fftfreq(len(fft_result), d=1 / sample_rate)

        max_amplitude_index = np.argmax(np.abs(fft_result[1:])) + 1

        return frequencies[max_amplitude_index]

    def unmerge_rt60_values(self, rt60_low, rt60_mid, rt60_high):
        self.view.display_rt60_values(rt60_low, rt60_mid, rt60_high, self.merge_rt60_values, self.unmerge_rt60_values)

    def get_audio_duration(self):
        # Check if audio_data is available in the model
        if self.model.audio_data is not None:
            audio_segment = AudioSegment(
                data=self.model.audio_data.tobytes(),
                sample_width=self.model.audio_data.dtype.itemsize,
                frame_rate=self.model.sample_rate,
                channels=1  # Assuming mono audio
            )
            return audio_segment.duration_seconds
        else:
            return 0

    def calculate_and_display_rt60_difference(self):
        # Get the RT60 values from the model
        rt60_low = np.atleast_1d(self.model.rt60_low)
        rt60_mid = np.atleast_1d(self.model.rt60_mid)
        rt60_high = np.atleast_1d(self.model.rt60_high)

        # Take the average of the RT60 values
        avg_rt60 = np.mean([np.mean(rt60_low), np.mean(rt60_mid), np.mean(rt60_high)])

        # Calculate the difference from the optimum reverb time (0.5 seconds)
        rt60_difference = avg_rt60 - 0.5

        self.view.display_rt60_values(rt60_low, rt60_mid, rt60_high, self.merge_rt60_values, self.unmerge_rt60_values,
                                      rt60_difference)

    def show_spectrogram(self):
        if self.model.audio_data is not None and self.model.sample_rate is not None:
            audio_data = self.model.audio_data
            sample_rate = self.model.sample_rate
            self.view.show_spectrogram(audio_data, sample_rate)
        else:
            print("Error: No audio data available.")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Scientific Python Interactive Data Acoustic Modeling")

    root.geometry("400x200")

    app = AudioController(root)
    root.mainloop()