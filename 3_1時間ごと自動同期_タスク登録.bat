@echo off
chcp 65001 >nul
title 1時間ごと自動同期タスクの登録

echo ======================================================================
echo    Windowsタスクスケジューラ登録: 1時間ごとのVault自動同期
echo ======================================================================
echo.

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$action = New-ScheduledTaskAction -Execute 'c:\business\prompt_vault_public\.venv\Scripts\pythonw.exe' -Argument 'c:\business\prompt_vault_public\sync_service.py' -WorkingDirectory 'c:\business\prompt_vault_public';" ^
  "$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 1);" ^
  "$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries;" ^
  "Register-ScheduledTask -TaskName 'PromptVault_AutoSync' -Action $action -Trigger $trigger -Settings $settings -Force;"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [OK] タスクスケジューラへの登録が完了しました！
    echo PC起動中、1時間ごとに完全自動で個人Vaultの新作が公開版へ同期されます。
) else (
    echo.
    echo [ERROR] 登録に失敗しました。
)

echo.
pause
