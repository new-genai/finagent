@echo off
title FinAgent Launcher
echo ==========================================
echo       DANG KHOI CHAY FINAGENT (BE & FE)
echo ==========================================

:: Chay Backend FastAPI o cua so rieng
start "FinAgent - Backend (FastAPI)" cmd /k "python -m uvicorn src.main:app --reload --host 127.0.0.1 --port 8000"

:: Chay Frontend Next.js o cua so rieng
start "FinAgent - Frontend (Next.js)" cmd /k "cd frontend && npm run dev"

echo.
echo Da kich hoat 2 server thanh cong!
echo Backend:  http://127.0.0.1:8000/docs
echo Frontend: http://localhost:3000
echo ==========================================
pause
