"""
predictor.py
Shared logic: loads the trained model and turns raw input
into score / pass-fail / grade predictions.
"""

import joblib
import numpy as np

model = joblib.load("model.joblib")
scaler = joblib.load("scaler.joblib")
FEATURES = joblib.load("features.joblib")

def grade_from_score(score):
    if score >= 90: return "A"
    if score >= 75: return "B"
    if score >= 60: return "C"
    if score >= 40: return "D"
    return "F"

def predict(data: dict):
    row = np.array([[data[f] for f in FEATURES]])
    row_scaled = scaler.transform(row)
    score = float(model.predict(row_scaled)[0])
    score = round(max(0, min(100, score)), 1)

    return {
        "predicted_score": score,
        "pass_fail": "Pass" if score >= 40 else "Fail",
        "grade": grade_from_score(score),
    }