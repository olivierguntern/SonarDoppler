# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import filedialog, messagebox
import os
from pydub import AudioSegment
import subprocess
import warnings
from pydub.exceptions import PydubException

class DopplerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Doppler Analysis")
        
        self.label = tk.Label(root, text="Choose an MP3 audio file for Doppler Analysis")
        self.label.pack(pady=10)

        self.button = tk.Button(root, text="Browse", command=self.browse_file)
        self.button.pack(pady=10)
        
        self.result_label = tk.Label(root, text="")
        self.result_label.pack(pady=10)

        # Spécifiez le chemin vers ffmpeg ici
        AudioSegment.converter = "C:/chemin/vers/ffmpeg.exe"

        # Ignorer l'avertissement de pydub concernant ffmpeg ou avconv
        warnings.filterwarnings("ignore", category=RuntimeWarning, message="Couldn't find ffmpeg or avconv")

    def browse_file(self):
        self.root.withdraw()  # Masquer la fenêtre principale
        self.filepath = filedialog.askopenfilename(filetypes=[("MP3 Files", "*.mp3")])
        if self.filepath:
            self.label.config(text=f"Selected MP3 File: {os.path.basename(self.filepath)}")
            self.convert_and_analyze()

    def convert_and_analyze(self):
        try:
            # Vérifier si le fichier MP3 existe
            if not os.path.exists(self.filepath):
                raise FileNotFoundError(f"MP3 file '{self.filepath}' not found.")

            # Convertir le fichier MP3 en WAV
            wav_filepath = os.path.splitext(self.filepath)[0] + '.wav'
            AudioSegment.from_mp3(self.filepath).export(wav_filepath, format="wav")
            self.filepath = wav_filepath

            # Assurez-vous que doppler_analysis.py est dans le même répertoire ou dans le chemin de recherche Python
            from doppler_analysis import DopplerAnalysis  
            analysis = DopplerAnalysis(self.filepath)
            analysis.calculate_average_frequency()
            analysis.identify_car_passages()
            speeds = analysis.calculate_speeds()
            analysis.generate_csv(speeds)
            self.result_label.config(text="Analysis Complete! Results saved to car_speeds.csv")
        except PydubException as e:
            # Gérer les erreurs spécifiques à pydub (y compris les problèmes de ffmpeg)
            messagebox.showerror("Conversion Error", f"Failed to convert MP3 to WAV: {str(e)}")
        except Exception as e:
            # Gérer toutes les autres erreurs
            messagebox.showerror("Error", f"Error: {str(e)}")
        finally:
            self.root.destroy()  # Détruire complètement la fenêtre après l'analyse

if __name__ == "__main__":
    root = tk.Tk()
    app = DopplerApp(root)
    root.mainloop()
