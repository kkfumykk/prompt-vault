@echo off
chcp 65001 >nul
title 1時間ごと自動同期タスクの解除

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "Unregister-ScheduledTask -TaskName 'PromptVault_AutoSync' -Confirm:$false -ErrorAction SilentlyContinue;"

echo [OK] タスクスケジューラの定期同期設定を解除しました。
pause
