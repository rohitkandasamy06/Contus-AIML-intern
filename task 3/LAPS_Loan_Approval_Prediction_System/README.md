# LAPS — Loan Approval Prediction System

A complete, real-time, user-friendly ML web application that predicts loan approval
using a **Random Forest** classifier, with a FastAPI backend and a clean HTML/CSS/JS frontend.

---

## 📁 Project Structure

```
loan-approval-app/
├── data/
│   └── loan_data.csv          # Practical synthetic dataset (5,000 rows)
├── model/
│   ├── train_model.py         # Trains & saves the Random Forest model
│   ├── model.pkl              # Trained model (generated)
│   ├── encoders.pkl           # Label encoders (generated)
│   ├── target_encoder.pkl     # Target label encoder (generated)
│   └── columns.pkl            # Feature column order (generated)
├── backend/
│   ├── app.py                 # FastAPI app — serves API + frontend
│   └── requirements.txt
└── frontend/
    ├── index.html
    ├── style.css
    └── script.js
```

## 📊 Dataset

`data/loan_data.csv` — 5,000 realistic loan applications with practical underwriting features:

| Column | Description |
|---|---|
| gender, married, dependents, education, self_employed | Applicant profile |
| applicant_income, coapplicant_income | Annual income (₹) |
| loan_amount, loan_term_months | Loan requested |
| credit_score | 300–900 (strongest predictor, like real CIBIL/FICO scores) |
| property_area | Urban / Semiurban / Rural |
| residential_assets_value, commercial_assets_value, bank_assets_value | Collateral / net worth |
| loan_status | Target: Approved / Rejected |

Approval logic factors in credit score, debt-to-income ratio, and total assets — mirroring
how real lenders underwrite loans — with realistic noise so the model isn't trivially 100% accurate.

## 🚀 Setup in VS Code

### 1. Open the project folder
Open `loan-approval-app/` in VS Code.

### 2. Create a virtual environment
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r backend/requirements.txt
```

### 4. Train the model
```bash
cd model
python train_model.py
```
This prints accuracy, classification report, and feature importances, then saves
`model.pkl`, `encoders.pkl`, `target_encoder.pkl`, `columns.pkl` into `model/`.

Expected output: **~77-90% accuracy** depending on random seed/tuning.

### 5. Run the app (backend + frontend together)
```bash
cd ../backend
uvicorn app:app --reload --port 8000
```

Open your browser at:
```
http://127.0.0.1:8000
```

That's it — **one server, one port**, serves both the API and the website.

API docs (Swagger UI) are available at:
```
http://127.0.0.1:8000/docs
```

## 🔌 API Reference

**GET** `/api/health` — health check

**POST** `/api/predict` — returns prediction
```json
{
  "gender": "Male",
  "married": "Yes",
  "dependents": 0,
  "education": "Graduate",
  "self_employed": "No",
  "applicant_income": 60000,
  "coapplicant_income": 20000,
  "loan_amount": 15000,
  "loan_term_months": 120,
  "credit_score": 780,
  "property_area": "Urban",
  "residential_assets_value": 500000,
  "commercial_assets_value": 0,
  "bank_assets_value": 200000
}
```

Response:
```json
{
  "approved": true,
  "status": "Approved",
  "confidence": 88.22,
  "approval_probability": 88.22,
  "top_factors": ["Credit Score", "Loan Amount", "Residential Assets", "Applicant Income", "Bank Assets"]
}
```

## 🧠 Why Random Forest

- Works directly on numeric + encoded categorical features — no scaling required
- `class_weight="balanced"` handles the realistic 60/40 approval imbalance
- Built-in feature importance → powers the "Top factors influencing this decision" explanation in the UI
- Robust, interpretable, well-suited for compliance-sensitive domains like lending

## ☁️ Deployment (optional next step)

- **Backend+Frontend (single service):** Deploy to **Render** or **Railway** — push this repo to
  GitHub, connect it, set start command to `uvicorn app:app --host 0.0.0.0 --port $PORT`.
- **Docker:** add a simple Dockerfile (ask if you want this generated) and deploy to any
  container host (Fly.io, AWS, Render, etc.)

## 🔁 Retraining with your own data

Replace `data/loan_data.csv` with your own data (keep the same column names), then re-run:
```bash
cd model
python train_model.py
```
The backend automatically picks up the new `model.pkl` on next restart.
