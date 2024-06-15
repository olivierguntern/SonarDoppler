
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
