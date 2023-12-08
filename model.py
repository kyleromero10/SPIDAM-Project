# model.py

class AudioModel:
    def __init__(self):
        self.file_path = None
        self.sample_rate = None
        self.audio_data = None
        self.rt60_low = None
        self.rt60_mid = None
        self.rt60_high = None

    def set_file_path(self, file_path):
        self.file_path = file_path

    def set_audio_data(self, sample_rate, audio_data):
        self.sample_rate = sample_rate
        self.audio_data = audio_data

    def set_rt60_values(self, rt60_low, rt60_mid, rt60_high):
        self.rt60_low = rt60_low
        self.rt60_mid = rt60_mid
        self.rt60_high = rt60_high
