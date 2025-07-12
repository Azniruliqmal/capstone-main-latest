@echo off
cd /d "C:\Users\User\Desktop\COHORT 3 PROJECT - GAMUDA AI\PROJECT\capstone-main-main\backend"
"C:/Users/User/Desktop/COHORT 3 PROJECT - GAMUDA AI/PROJECT/capstone-main-main/.venv/Scripts/python.exe" -m uvicorn api.api:app --reload --host 0.0.0.0 --port 8000
pause
