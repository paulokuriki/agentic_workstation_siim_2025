# constants.py

SAMPLE_CASES = [
    {"id": 101, "url": "https://prod-images-static.radiopaedia.org/images/1371188/0a1f5edc85aa58d5780928cb39b08659c1fc4d6d7c7dce2f8db1d63c7c737234_big_gallery.jpeg"},
    {"id": 102, "url": "https://prod-images-static.radiopaedia.org/images/1420387/6f63736ff837ff7c5a736b35aba6ab_big_gallery.jpeg"},
    {"id": 103, "url": "https://prod-images-static.radiopaedia.org/images/8686421/17baee9bfb9018e3d109ec63cb380e_big_gallery.jpeg"}
]

# MODEL CONFIG
LLM_MODEL_WORKFLOW_AGENT = "gemini-2.0-flash"
LLM_MODEL_REPORT_AGENT = "gemini-2.0-flash"

# We will crop dictations larger than 10 s
MAX_DURATION_AUDIO = 10

# List of LLMs to test
# gemini-2.0-flash                    Input $0.10   Output $0.40
# gemini-2.0-flash-lite-preview-02-05 Input $0.075  Output $0.30


CASES = [
    {
        "Study ID": 101,
        "Patient MRN": "101040",
        "Date": "2024-03-01",
        "Modality": "Chest X-Ray",
        #"Report": "Normal heart size. Clear lungs without consolidation or effusion. No evidence of pneumothorax.",
        #"Radiologist": "Dr. Emily Carter",
        "medical_charts": [
            {"Date": "2024-02-15", "Reason": "Routine annual physical exam", "History": "No complaints. Patient in good overall health.", "Vitals": "BP: 118/76, HR: 72 bpm, Temp: 98.6°F", "physical_exam": "Clear lung sounds, heart sounds normal.", "assessment": "Healthy adult, routine screening only.", "Plan": "Continue regular follow-up."},
            {"Date": "2024-01-10", "Reason": "Persistent cough lasting over 2 weeks", "History": "Dry cough, no fever, occasional wheezing.", "Vitals": "BP: 120/80, HR: 78 bpm, Temp: 99°F", "Diagnosis": "Mild bronchitis", "Treatment": "Prescribed antibiotics for 7 days, advised increased fluid intake."},
            {"Date": "2023-12-20", "Reason": "Chest discomfort during exercise", "History": "Brief episodes of chest tightness, relieved by rest.", "Vitals": "BP: 125/82, HR: 70 bpm, Temp: 98.7°F", "tests": "Normal ECG", "assessment": "Likely musculoskeletal in nature.", "Recommendations": "Recommended ibuprofen and follow-up in one month if symptoms persist."},
        ]
    },
    {
        "Study ID": 102,
        "Patient MRN": "102040",
        "Date": "2024-03-01",
        "Modality": "Chest X-Ray",
        #"Report": "Mild cardiomegaly with slight prominence of pulmonary vasculature suggestive of mild congestive heart failure. No acute infiltrates or effusions.",
        #"Radiologist": "Dr. Michael Zhang",
        "medical_charts": [
            {"Date": "2024-02-10", "Reason": "Shortness of breath on exertion", "History": "Fatigue and mild leg swelling.", "Vitals": "BP: 140/90, HR: 88 bpm, Temp: 98.4°F", "Diagnosis": "Early congestive heart failure", "Treatment": "Initiated diuretic therapy, recommended lifestyle modifications including sodium restriction."},
            {"Date": "2024-01-05", "Reason": "Follow-up cardiovascular assessment", "History": "Improvement in symptoms, no significant dyspnea.", "Vitals": "BP: 125/80, HR: 70 bpm, Temp: 98.5°F", "Assessment": "Stable heart function.", "Plan": "Continue medications, schedule echocardiogram in six months."},
            {"Date": "2023-12-20", "Reason": "Annual cardiovascular screening", "History": "Family history of heart disease, patient asymptomatic.", "Vitals": "BP: 130/85, HR: 68 bpm, Temp: 98.5°F", "Findings": "Slight increase in heart size noted on imaging", "Recommendations": "Annual imaging follow-up, monitor closely for symptom changes."},
        ]
    },
    {
        "Study ID": 103,
        "Patient MRN": "103010",
        "Date": "2024-03-01",
        "Modality": "Chest X-Ray",
        #"Report": "Bilateral lower lobe infiltrates consistent with early pneumonia. Small left pleural effusion present.",
        #"Radiologist": "Dr. Priya Nair",
        "medical_charts": [
            {"Date": "2024-02-20", "Reason": "Persistent cough and fever lasting 5 days", "History": "Productive cough with yellow sputum, fever peaking at 101°F.", "Vitals": "BP: 122/78, HR: 90 bpm, Temp: 101°F", "Diagnosis": "Early pneumonia", "Treatment": "Initiated broad-spectrum antibiotics for 10 days, hydration advised."},
            {"Date": "2024-02-01", "Reason": "Routine respiratory follow-up", "History": "Patient recovered from previous cold, no current respiratory distress.", "Vitals": "BP: 118/78, HR: 72 bpm, Temp: 98.4°F", "assessment": "Stable respiratory status.", "Plan": "Continue routine monitoring."},
            {"Date": "2023-12-20", "Reason": "Cold symptoms", "History": "Symptoms of nasal congestion, mild sore throat.", "Vitals": "BP: 119/78, HR: 74 bpm, Temp: 99.1°F", "Diagnosis": "Viral upper respiratory infection (URI)", "Management": "Advised rest, increased fluid intake, and symptomatic management with over-the-counter remedies."},
        ]
    }
]


