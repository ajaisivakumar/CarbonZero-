@echo off
title CarbonZero AI Agent
cd /d "D:\Edunet_Project"

set "PYTHON_PATH=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"

if not exist "%PYTHON_PATH%" (
    set "PYTHON_PATH=python"
)

echo ============================================================
echo   Starting CarbonZero: AI Sustainability & EV Agent
echo ============================================================
echo Checking and installing dependencies...
"%PYTHON_PATH%" -m pip install -r requirements.txt

echo.
echo Launching Streamlit Dashboard...
"%PYTHON_PATH%" -m streamlit run app.py

pause
