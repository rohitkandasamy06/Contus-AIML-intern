"""
train_model.py
Trains a RandomForestRegressor to predict a student's final score.
"""

import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score

FEATURES = [
    "study_hours_per_day",
    "attendance_percent",
    "previous_score",
    "assignments_completed_percent",
    "sleep_hours",
    "extra_activities",
    "parental_support",
    "internet_access",
]
TARGET = "final_score"

def main():
    df = pd.read_csv("student_data.csv")

    X = df[FEATURES]
    y = df[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model = RandomForestRegressor(
        n_estimators=200, max_depth=8, random_state=42, n_jobs=-1
    )
    model.fit(X_train_scaled, y_train)

    preds = model.predict(X_test_scaled)
    mae = mean_absolute_error(y_test, preds)
    r2 = r2_score(y_test, preds)
    print(f"Test MAE   : {mae:.2f} marks")
    print(f"Test R^2   : {r2:.3f}")

    actual_pass = (y_test >= 40).astype(int)
    pred_pass = (preds >= 40).astype(int)
    acc = (actual_pass == pred_pass).mean()
    print(f"Pass/Fail accuracy: {acc*100:.1f}%")

    importances = pd.Series(model.feature_importances_, index=FEATURES)
    print("\nFeature importance:")
    print(importances.sort_values(ascending=False).round(3))

    joblib.dump(model, "model.joblib")
    joblib.dump(scaler, "scaler.joblib")
    joblib.dump(FEATURES, "features.joblib")
    print("\nSaved model.joblib, scaler.joblib, features.joblib")

if __name__ == "__main__":
    main()