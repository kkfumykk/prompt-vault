@echo off
chcp 65001 >nul
title AI Prompt & Art Gallery - Cloudflare Tunnel ネット公開

echo ======================================================================
echo       AI Prompt & Art Gallery - 世界中へワンクリック公開中！
echo ======================================================================
echo.

cd /d "%~dp0"

if not exist "bin\cloudflared.exe" (
    echo [ERROR] bin\cloudflared.exe が見つかりません。
    pause
    exit /b 1
)

echo [1/2] ローカルサーバー (ポート 8080) の状態を確認しています...
start "" /min .venv\Scripts\python.exe launcher_public.py

echo [2/2] Cloudflare Tunnel による安全なHTTPS公開URLを発行しています...
echo.
echo ----------------------------------------------------------------------
echo ※数秒後に下記に「https://xxxx.trycloudflare.com」というURLが表示されます！
echo  そのURLをXのポストやプロフィール、スマホのブラウザで共有してください。
echo ※この画面を閉じるとネット公開が停止します。
echo ----------------------------------------------------------------------
echo.

bin\cloudflared.exe tunnel --url http://127.0.0.1:8080

pause
