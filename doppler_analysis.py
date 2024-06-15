# -*- coding: utf-8 -*-
import librosa
import numpy as np
import pandas as pd
import datetime

# Constants
SPEED_OF_SOUND = 343  # m/s

class DopplerAnalysis:
    def __init__(self, audio_file, mic_distance=1.5, sample_rate=44100):
        self.audio_file = audio_file
        self.mic_distance = mic_distance
        self.sample_rate = sample_rate
        self.data, self.sr = librosa.load(audio_file, sr=sample_rate)
        self.timestamps = np.arange(len(self.data)) / self.sr
        self.freqs = []
        self.intensities = []
        self.cars = []

    def calculate_average_frequency(self):
        # Calculate the frequency and intensity at each time step
        pitches, magnitudes = librosa.piptrack(y=self.data, sr=self.sr)
        for t in range(magnitudes.shape[1]):
            index = magnitudes[:, t].argmax()
            pitch = pitches[index, t]
            if pitch > 0:  # Only consider valid pitches
                self.freqs.append(pitch)
                self.intensities.append(magnitudes[index, t])
            else:
                self.freqs.append(0)
                self.intensities.append(0)

    def identify_car_passages(self):
        # Detect peaks in intensity to find car passages
        peak_threshold = np.mean(self.intensities) + 2 * np.std(self.intensities)
        peaks = np.where(self.intensities > peak_threshold)[0]
        
        current_car = []
        for i in range(len(peaks) - 1):
            if peaks[i+1] - peaks[i] > self.sr:  # More than 1 second gap indicates a new car
                if current_car:
                    self.cars.append(current_car)
                    current_car = []
            current_car.append(peaks[i])
        if current_car:
            self.cars.append(current_car)

    def calculate_speeds(self):
        speeds = []
        for car in self.cars:
            peak_intensity_index = car[np.argmax([self.intensities[i] for i in car])]
            peak_frequency = self.freqs[peak_intensity_index]
            
            # Assuming the peak frequency is the true engine frequency without Doppler effect
            f_real = peak_frequency
            
            f_a = np.mean([self.freqs[i] for i in car if i < peak_intensity_index])
            f_r = np.mean([self.freqs[i] for i in car if i > peak_intensity_index])
            
            if f_a > f_r:
                # Car moving from left to right
                v_s = SPEED_OF_SOUND * ((f_a - f_r) / (2 * f_real))
            else:
                # Car moving from right to left, need to account for longer distance
                v_s = SPEED_OF_SOUND * ((f_r - f_a) / (2 * f_real))
            
            speeds.append((peak_intensity_index / self.sr, v_s))
        return speeds

    def generate_csv(self, speeds):
        df = pd.DataFrame(speeds, columns=['Time (s)', 'Speed (m/s)'])
        df['Time (s)'] = df['Time (s)'].apply(lambda x: str(datetime.timedelta(seconds=x)))
        df.to_csv('car_speeds.csv', index=False)
        print(df)
