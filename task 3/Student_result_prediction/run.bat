@echo off
title Student Result Predictor
cd /d "%~dp0"

echo ============================================
echo  Student Result Prediction System - Launcher
echo ============================================
echo.

echo [1/3] Installing required packages (this may take a moment the first time)...
pip install -r requirements.txt --quiet

echo [2/3] Checking trained model...
if not exist "model.joblib" (
    echo Model not found. Training now...
    python train_model.py
) else (
    echo Model already trained. Skipping training.
)

echo [3/3] Starting the web app...
echo.
echo Once you see "Running on http://127.0.0.1:5050", your browser will open automatically.
echo Press CTRL+C in this window to stop the server when you're done.
echo.

start "" cmd /c "timeout /t 4 /nobreak >nul && start http://127.0.0.1:5050"
python app.py

pause