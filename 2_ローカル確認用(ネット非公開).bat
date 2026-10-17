@echo off
chcp 65001 >nul
title AI Prompt Gallery (Public Edition)

cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found in .venv!
    pause
    exit /b 1
)

.venv\Scripts\python.exe launcher_public.py
