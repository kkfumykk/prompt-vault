@echo off
chcp 65001 >nul
title Prompt Vault 同期＆クラウド自動反映ツール

echo ======================================================================
echo    個人用Vault から 公開版 へのデータ同期 ＆ クラウド自動公開
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
echo ======================================================================
echo ※新規イラストがあった場合、自動でGitHub経由でクラウドに反映されます。
echo ======================================================================
echo.
pause
