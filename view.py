# view.py
import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
import librosa.util
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.signal import spectrogram
plt.switch_backend("TkAgg")

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

        #Merge Button
        self.merge_button = tk.Button(root, text="Merge Graphs", command=lambda: None)
        self.merge_button.pack(pady=10)

        #Spectrogram Button
        self.spectrogram_button = tk.Button(root, text="Show Spectrogram", command=self.controller.show_spectrogram)
        self.spectrogram_button.pack(pady=10)

        self.spectrogram_frame = tk.Frame(root)
        self.spectrogram_frame.pack()

        # Initialize the label for RT60 difference
        self.initialize_rt60_difference_label()


    def display_file_name(self, file_name):
        self.result_label.config(text=f"File: {file_name}")

    def display_waveform(self, audio_data, sample_rate):
        # Convert audio_data to floating-point format
        audio_data_float = librosa.util.normalize(audio_data.astype(float))

        # Plot the waveform with units on axes
        time = np.arange(0, len(audio_data_float)) / sample_rate  # Time in seconds
        plt.figure(figsize=(10, 4))
        plt.plot(time, audio_data_float)
        plt.title('Waveform')
        plt.xlabel('Time (seconds)')
        plt.ylabel('Amplitude')

        # Compute the highest resonance frequency
        highest_resonance_freq = self.controller.compute_highest_resonance(audio_data, sample_rate)

        # Add text for highest resonance frequency
        plt.text(0.5, 0.92, f'Highest Resonance: {highest_resonance_freq:.2f} Hz', transform=plt.gca().transAxes,
                 color='black', fontsize=12, fontweight='bold', ha='center')

        # Add text for time duration
        audio_duration = len(audio_data_float) / sample_rate
        plt.text(0.5, 0.85, f'Duration: {audio_duration:.2f} seconds', transform=plt.gca().transAxes,
                 color='black', fontsize=12, fontweight='bold', ha='center')

        plt.subplots_adjust(bottom=0.2)

        plt.show()

    def compute_highest_resonance(self, audio_data, sample_rate):
        # Compute the Fast Fourier Transform (FFT)
        fft_result = np.fft.fft(audio_data)

        frequencies = np.fft.fftfreq(len(fft_result), d=1 / sample_rate)

        max_amplitude_index = np.argmax(np.abs(fft_result[1:])) + 1

        return frequencies[max_amplitude_index]

    def display_rt60_values(self, rt60_low, rt60_mid, rt60_high, merge_function, unmerge_function,rt60_difference=None):
        # Convert scalar values to arrays
        rt60_low = np.atleast_1d(rt60_low)
        rt60_mid = np.atleast_1d(rt60_mid)
        rt60_high = np.atleast_1d(rt60_high)

        # Determine the minimum length
        min_len = min(len(rt60_low), len(rt60_mid), len(rt60_high))

        # Get the duration of the audio file
        audio_duration = self.controller.get_audio_duration()

        # Create subplots for the three individual graphs
        fig, axs = plt.subplots(3, 1, figsize=(10, 12))

        time = np.linspace(0, audio_duration, min_len, endpoint=False)  # Use endpoint=False

        # Plot individual graphs
        axs[0].plot(time, rt60_low[:min_len], label='Low Frequency', color='blue')
        axs[1].plot(time, rt60_mid[:min_len], label='Mid Frequency', color='green')
        axs[2].plot(time, rt60_high[:min_len], label='High Frequency', color='red')

        # Set y-axis limits to better visualize short RT60 values
        axs[0].set_ylim(0, 0.1)
        axs[1].set_ylim(0, 0.1)
        axs[2].set_ylim(0, 0.1)

        axs[0].set_title('RT60 for Low Frequency')
        axs[0].set_xlabel('Time (seconds)')
        axs[0].set_ylabel('Power (dB)')
        axs[0].legend()

        axs[1].set_title('RT60 for Mid Frequency')
        axs[1].set_xlabel('Time (seconds)')
        axs[1].set_ylabel('Power (dB)')
        axs[1].legend()

        axs[2].set_title('RT60 for High Frequency')
        axs[2].set_xlabel('Time (seconds)')
        axs[2].set_ylabel('Power (dB)')
        axs[2].legend()

        plt.tight_layout()

        self.merge_button.config(command=lambda: merge_function(rt60_low, rt60_mid, rt60_high))

        # Display RT60 difference if available
        if rt60_difference is not None:
            # Add text for RT60 difference
            plt.text(0.5, 0.78, f'RT60 Difference: {rt60_difference:.2f} seconds', transform=plt.gca().transAxes,
                     color='black', fontsize=12, fontweight='bold', ha='center')

        plt.show()


    def merge_rt60_values(self, rt60_low, rt60_mid, rt60_high):
        # Create time array for x-axis
        time = np.arange(0, len(rt60_low))

        # Create a new figure for the merged graph
        plt.figure(figsize=(10, 4))

        # Plot the merged graph
        plt.plot(time, rt60_low, label='Low Frequency', color='blue')
        plt.plot(time, rt60_mid, label='Mid Frequency', color='green')
        plt.plot(time, rt60_high, label='High Frequency', color='red')

        plt.title('Merged RT60 for Low, Mid, High Frequencies')
        plt.xlabel('Time (seconds)')
        plt.ylabel('Power (dB)')
        plt.legend()

        plt.show()

    def display_rt60_difference(self, rt60_difference):
        rt60_difference_text = f"Difference: {rt60_difference:.2f} seconds"
        self.rt60_difference_label.config(text=rt60_difference_text)

    def initialize_rt60_difference_label(self):
        self.rt60_difference_label = tk.Label(self.root, text="")
        self.rt60_difference_label.pack()

    def show_spectrogram(self, audio_data, sample_rate):
        # Compute the spectrogram
        f, t, Sxx = spectrogram(audio_data, fs=sample_rate)

        fig, ax = plt.subplots(figsize=(10, 4))
        ax.pcolormesh(t, f, 10 * np.log10(Sxx), shading='auto')
        ax.set_title('Spectrogram')
        ax.set_xlabel('Time (seconds)')
        ax.set_ylabel('Frequency (Hz)')
        ax.figure.colorbar(ax.collections[0], label='Power/Frequency (dB/Hz)')

        canvas = FigureCanvasTkAgg(fig, master=self.spectrogram_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()

        plt.show()
