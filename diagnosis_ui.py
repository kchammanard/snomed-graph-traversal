import tkinter as tk
from tkinter import messagebox
from keywordmatcher import KeywordMatcher
from diagnosis import DifferentialDiagnosis
import json 

class DifferentialDiagnosisInterface:
    def __init__(self, symptom_names):
        self.matcher = KeywordMatcher(symptom_names, threshold=90)
        self.diagnosis = DifferentialDiagnosis()

        self.root = tk.Tk()
        self.root.title("Differential Diagnosis")
        self.root.geometry("700x500")

        self.label = tk.Label(self.root, text="คุณมีอาการประมาณไหน:", font=("Arial", 12))
        self.label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.text_box = tk.Text(self.root, height=4)
        self.text_box.grid(row=1, column=0, padx=10, pady=5)

        self.button = tk.Button(self.root, text="วินิจฉัย", font=("Arial", 12), command=self.match_symptoms)
        self.button.grid(row=2, column=0, padx=10, pady=5)

        self.symptom_checkboxes = []
        self.diagnosis_button = None

    def match_symptoms(self):
        user_input = self.text_box.get("1.0", tk.END).strip()

        if not user_input:
            messagebox.showinfo("Error", "Please enter some symptoms.")
            return

        matching_keywords = self.matcher.find_matching_keywords(user_input)
        self.display_symptom_checkboxes(matching_keywords)

    def display_symptom_checkboxes(self, matching_keywords):
        self.clear_checkboxes()
        
        for i, symptom in enumerate(set(matching_keywords)):
            var = tk.IntVar()
            checkbox = tk.Checkbutton(self.root, text=symptom, variable=var)
            checkbox.grid(row=i + 3, column=0, padx=10, pady=2, sticky="w")
            self.symptom_checkboxes.append((symptom, var))

        self.diagnosis_button = tk.Button(self.root, text="Calculate Diagnosis", command=self.calculate)
        self.diagnosis_button.grid(row=len(matching_keywords) + 3, column=0, padx=10, pady=5)

    def clear_checkboxes(self):
        for symptom, var in self.symptom_checkboxes:
            var.set(0)
        self.symptom_checkboxes.clear()

        if self.diagnosis_button:
            self.diagnosis_button.grid_forget()

    def calculate(self):
        user_symptoms = [symptom for symptom, var in self.symptom_checkboxes if var.get()]

        if not user_symptoms:
            messagebox.showinfo("Error", "Please select at least one symptom.")
            return

        results, contradictory_symptoms, missing_symptoms = self.diagnosis.calculate_diagnosis_probabilities(user_symptoms)
        self.display_results(user_symptoms, results, contradictory_symptoms, missing_symptoms)

    def display_results(self, user_symptoms, results, contradictory_symptoms, missing_symptoms):
        result_text = "User Symptoms:\n" + ", ".join(user_symptoms) + "\n\n"
        result_text += "Contradictory Symptoms:\n" + ", ".join(contradictory_symptoms) + "\n\n"
        result_text += "Missing Symptoms:\n" + ", ".join(missing_symptoms) + "\n\n"
        result_text += "Diagnosis Probabilities:\n"
        for diagnosis, probability in results.items():
            result_text += f"{diagnosis}: {probability:.2f}%\n"

        messagebox.showinfo("Differential Diagnosis Results", result_text)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    with open('data/fever.json', 'r', encoding='utf-8') as f:
        symptom_names = json.load(f)

    interface = DifferentialDiagnosisInterface(symptom_names)
    interface.run()
