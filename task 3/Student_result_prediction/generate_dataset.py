"""
generate_dataset.py
Creates a synthetic but realistic student performance dataset
and saves it as student_data.csv
"""

import numpy as np
import pandas as pd

np.random.seed(42)
N = 1500

study_hours = np.clip(np.random.normal(4, 2.2, N), 0, 12)
attendance = np.clip(np.random.normal(78, 14, N), 30, 100)
previous_score = np.clip(np.random.normal(65, 15, N), 20, 100)
assignments_completed = np.clip(np.random.normal(75, 18, N), 0, 100)
sleep_hours = np.clip(np.random.normal(6.5, 1.3, N), 3, 10)
extra_activities = np.random.choice([0, 1], size=N, p=[0.6, 0.4])
parental_support = np.random.choice([1, 2, 3], size=N, p=[0.25, 0.5, 0.25])
internet_access = np.random.choice([0, 1], size=N, p=[0.2, 0.8])

final_score = (
    0.35 * (study_hours * 8)
    + 0.30 * attendance
    + 0.20 * previous_score
    + 0.10 * assignments_completed
    + 1.5 * sleep_hours
    + 3 * extra_activities
    + 4 * parental_support
    + 2 * internet_access
    - 25
    + np.random.normal(0, 6, N)
)
final_score = np.clip(final_score, 0, 100).round(1)

df = pd.DataFrame({
    "study_hours_per_day": study_hours.round(1),
    "attendance_percent": attendance.round(1),
    "previous_score": previous_score.round(1),
    "assignments_completed_percent": assignments_completed.round(1),
    "sleep_hours": sleep_hours.round(1),
    "extra_activities": extra_activities,
    "parental_support": parental_support,
    "internet_access": internet_access,
    "final_score": final_score,
})

df.to_csv("student_data.csv", index=False)
print(f"Saved student_data.csv with {len(df)} rows")
print(df.head())