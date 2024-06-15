import os
import sys
import subprocess
import urllib.request
import zipfile

def install_ffmpeg():
    ffmpeg_url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
    ffmpeg_zip_path = "ffmpeg.zip"
    ffmpeg_extract_path = "ffmpeg"

    # Télécharger le fichier ZIP de ffmpeg
    print("Téléchargement de ffmpeg...")
    urllib.request.urlretrieve(ffmpeg_url, ffmpeg_zip_path)
    print("Téléchargement terminé.")

    # Extraire le fichier ZIP
    print("Extraction de ffmpeg...")
    with zipfile.ZipFile(ffmpeg_zip_path, 'r') as zip_ref:
        zip_ref.extractall(ffmpeg_extract_path)
    print("Extraction terminée.")

    # Trouver le chemin du dossier bin
    for root, dirs, files in os.walk(ffmpeg_extract_path):
        if "bin" in dirs:
            ffmpeg_bin_path = os.path.join(root, "bin")
            break

    # Ajouter le chemin au PATH
    print("Ajout de ffmpeg au PATH...")
    os.environ["PATH"] += os.pathsep + ffmpeg_bin_path
    print("ffmpeg ajouté au PATH.")

    # Vérifier l'installation de ffmpeg
    try:
        subprocess.check_call(["ffmpeg", "-version"])
        print("ffmpeg installé avec succès.")
    except subprocess.CalledProcessError:
        print("Erreur lors de l'installation de ffmpeg.")

def install_libraries():
    libraries = ['librosa', 'numpy', 'pandas', 'pydub', 'tk']
    subprocess.check_call([sys.executable, "-m", "pip", "install"] + libraries)

def create_files():
    doppler_analysis_code = """# -*- coding: utf-8 -*-
import librosa
import numpy as np
import pandas as pd
from pydub import AudioSegment
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
"""

    doppler_app_code = """# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import filedialog, messagebox
import os

class DopplerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Doppler Analysis")
        
        self.label = tk.Label(root, text="Choose an audio file for Doppler Analysis")
        self.label.pack(pady=10)

        self.button = tk.Button(root, text="Browse", command=self.browse_file)
        self.button.pack(pady=10)
        
        self.result_label = tk.Label(root, text="")
        self.result_label.pack(pady=10)

    def browse_file(self):
        self.filepath = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3 *.wav")])
        if self.filepath:
            self.label.config(text=f"Selected File: {os.path.basename(self.filepath)}")
            self.perform_analysis()

    def perform_analysis(self):
        try:
            from doppler_analysis import DopplerAnalysis
            analysis = DopplerAnalysis(self.filepath)
            analysis.calculate_average_frequency()
            analysis.identify_car_passages()
            speeds = analysis.calculate_speeds()
            analysis.generate_csv(speeds)
            self.result_label.config(text="Analysis Complete! Results saved to car_speeds.csv")
            self.root.quit()  # Fermer la fenêtre après l'analyse
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = DopplerApp(root)
    root.mainloop()
"""

    with open('doppler_analysis.py', 'w', encoding='utf-8') as f:
        f.write(doppler_analysis_code)

    with open('doppler_app.py', 'w', encoding='utf-8') as f:
        f.write(doppler_app_code)

# Installation de ffmpeg, des bibliothèques et création des fichiers
install_ffmpeg()
install_libraries()
create_files()

print("Setup complete. You can now run 'python doppler_app.py' to start the application.")
