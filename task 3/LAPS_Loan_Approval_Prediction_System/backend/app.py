import os
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "..", "model")
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend")

app = FastAPI(title="LAPS - Loan Approval Prediction System API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

model = joblib.load(os.path.join(MODEL_DIR, "model.pkl"))
encoders = joblib.load(os.path.join(MODEL_DIR, "encoders.pkl"))
target_le = joblib.load(os.path.join(MODEL_DIR, "target_encoder.pkl"))
columns = joblib.load(os.path.join(MODEL_DIR, "columns.pkl"))


class LoanApplication(BaseModel):
    gender: str = Field(..., examples=["Male"])
    married: str = Field(..., examples=["Yes"])
    dependents: int = Field(..., ge=0, le=10)
    education: str = Field(..., examples=["Graduate"])
    self_employed: str = Field(..., examples=["No"])
    applicant_income: float = Field(..., gt=0)
    coapplicant_income: float = Field(..., ge=0)
    loan_amount: float = Field(..., gt=0)
    loan_term_months: int = Field(..., gt=0)
    credit_score: float = Field(..., ge=300, le=900)
    property_area: str = Field(..., examples=["Urban"])
    residential_assets_value: float = Field(..., ge=0)
    commercial_assets_value: float = Field(..., ge=0)
    bank_assets_value: float = Field(..., ge=0)


@app.get("/api/health")
def health():
    return {"status": "running", "message": "LAPS - Loan Approval Prediction System API is live"}


@app.post("/api/predict")
def predict(application: LoanApplication):
    data = application.dict()
    df = pd.DataFrame([data])

    for col, le in encoders.items():
        if col in df.columns:
            try:
                df[col] = le.transform(df[col].astype(str))
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid value for '{col}'. Allowed: {list(le.classes_)}"
                )

    df = df[columns]

    pred = model.predict(df)[0]
    prob = model.predict_proba(df)[0]
    status = target_le.inverse_transform([pred])[0]
    approved_idx = list(target_le.classes_).index("Approved")

    # Top contributing factors (simple importance-based explanation)
    importances = dict(zip(columns, model.feature_importances_))
    top_factors = sorted(importances.items(), key=lambda x: -x[1])[:5]
    factor_labels = {
        "credit_score": "Credit Score",
        "loan_amount": "Loan Amount",
        "applicant_income": "Applicant Income",
        "residential_assets_value": "Residential Assets",
        "bank_assets_value": "Bank Assets",
        "coapplicant_income": "Coapplicant Income",
        "dependents": "Number of Dependents",
        "loan_term_months": "Loan Term",
        "education": "Education",
        "commercial_assets_value": "Commercial Assets",
        "property_area": "Property Area",
        "gender": "Gender",
        "married": "Marital Status",
        "self_employed": "Self Employment Status",
    }
    top_factors_named = [factor_labels.get(f, f) for f, _ in top_factors]

    return {
        "approved": bool(status == "Approved"),
        "status": status,
        "confidence": round(float(prob[pred]) * 100, 2),
        "approval_probability": round(float(prob[approved_idx]) * 100, 2),
        "top_factors": top_factors_named
    }


# Serve frontend
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
