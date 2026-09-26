@echo off
title TruVex AI - AI Against Misinformation & Digital Trust
echo ============================================================
echo   Starting TruVex AI Unified Platform...
echo ============================================================
if exist "%~dp0.venv\Scripts\python.exe" (
    "%~dp0.venv\Scripts\python.exe" "%~dp0run.py"
) else (
    python "%~dp0run.py"
)
