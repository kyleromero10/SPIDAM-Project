# SPIDAM
 
This program measures and analyzes reverberation time in a given audio file (if the file is not .wav, it will be converted to .wav) and plots the data as multiple different graph, as well as displaying the spectogram of the file.

This program exists so that users can graph audio files and use the data as needed.

## Usage

When you run the controller.py program a new GUI will open. Make sure you downloaded the requirements from requirements.txt.

Click on "Load Audio File" and your files will be opened. Click on the audio file you want to graph and click "Open" on the bottom right of the window. When the file loads, a waveform graph will appear. Clicking on the other three buttons will cause other graphs to appear. The "Plot RT60" button will cause low, mid, and high frequency graphs to appear. The "Merge Graphs" button will cause the low, mid, and high frequencies graphs to merge into one graph. Finally, the "Show Spectogram" button will cause a spectrogram of your file to appear. During the testing of our program, we had some errors displaying the plots the first time a file was loaded. Reloading the file or loading a different file will fix the issue. Also, the spectogram does not work for all audio files.
