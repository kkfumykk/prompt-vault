@echo off
chcp 65001 >nul
title Prompt Vault 同期ツール

echo ======================================================================
echo    個人用Vault から 公開版Gallery へのデータ同期 (増分コピー)
echo ======================================================================
echo.

cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Python仮想環境が見つかりません。
    pause
    exit /b 1
)

.venv\Scripts\python.exe sync_service.py

echo.
echo 同期処理が完了しました。
timeout /t 3 >nul
