# view.py
import tkinter as tk
import numpy as np
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

        # Create the Merge Button and set its command attribute to a dummy function initially
        self.merge_button = tk.Button(root, text="Merge Graphs", command=lambda: None)
        self.merge_button.pack(pady=10)

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

        # Move the text below the graph
        plt.subplots_adjust(bottom=0.2)

        # Add text for highest resonance frequency
        plt.text(0.5, 0, f'Highest Resonance: {highest_resonance_freq:.2f} Hz', transform=plt.gca().transAxes,
                 color='black', fontsize=12, fontweight='bold', ha='center')

        plt.show()

    def compute_highest_resonance(self, audio_data, sample_rate):
        # Compute the Fast Fourier Transform (FFT)
        fft_result = np.fft.fft(audio_data)

        # Calculate the frequencies corresponding to the FFT result
        frequencies = np.fft.fftfreq(len(fft_result), d=1 / sample_rate)

        # Find the index of the maximum amplitude (excluding DC component)
        max_amplitude_index = np.argmax(np.abs(fft_result[1:])) + 1

        # Return the frequency corresponding to the maximum amplitude
        return frequencies[max_amplitude_index]

    def display_rt60_values(self, rt60_low, rt60_mid, rt60_high, merge_function, unmerge_function):
        # Convert scalar values to arrays
        rt60_low = np.atleast_1d(rt60_low)
        rt60_mid = np.atleast_1d(rt60_mid)
        rt60_high = np.atleast_1d(rt60_high)

        print("RT60 Low array:", rt60_low)
        print("RT60 Mid array:", rt60_mid)
        print("RT60 High array:", rt60_high)

        # Determine the minimum length among the arrays
        min_len = min(len(rt60_low), len(rt60_mid), len(rt60_high))

        # Get the duration of the audio file using sound_duration
        audio_duration = self.controller.get_audio_duration()

        # Create subplots for the three individual graphs
        fig, axs = plt.subplots(3, 1, figsize=(10, 12))

        # Create time array for x-axis starting from zero and ending at audio duration
        time = np.linspace(0, audio_duration, min_len, endpoint=False)  # Use endpoint=False

        # Plot individual graphs
        axs[0].plot(time, rt60_low[:min_len], label='Low Frequency', color='blue')
        axs[1].plot(time, rt60_mid[:min_len], label='Mid Frequency', color='green')
        axs[2].plot(time, rt60_high[:min_len], label='High Frequency', color='red')

        # Set y-axis limits to better visualize short RT60 values
        axs[0].set_ylim(0, 0.1)  # Adjust the upper limit as needed
        axs[1].set_ylim(0, 0.1)
        axs[2].set_ylim(0, 0.1)

        # Set titles and labels for individual graphs
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

        # Adjust layout to prevent clipping of titles and labels
        plt.tight_layout()

        # Update the command attribute of the Merge Button
        self.merge_button.config(command=lambda: merge_function(rt60_low, rt60_mid, rt60_high))

        # Show the plots
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

        # Set title and labels for the merged graph
        plt.title('Merged RT60 for Low, Mid, High Frequencies')
        plt.xlabel('Time (seconds)')
        plt.ylabel('Power (dB)')
        plt.legend()

        # Show the merged plot
        plt.show()