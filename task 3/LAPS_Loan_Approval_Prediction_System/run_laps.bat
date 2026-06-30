@echo off
title LAPS - Loan Approval Prediction System
echo ============================================
echo   Starting LAPS - Loan Approval Prediction System
echo ============================================

cd /d "%~dp0"

if not exist "venv\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate.bat

echo Installing/checking dependencies...
pip install -r backend\requirements.txt -q

if not exist "model\model.pkl" (
    echo Training model for the first time...
    cd model
    python train_model.py
    cd ..
)

echo.
echo Starting server...
echo Open your browser at: http://127.0.0.1:8000
echo.

start http://127.0.0.1:8000
cd backend
python -m uvicorn app:app --host 127.0.0.1 --port 8000

pause
