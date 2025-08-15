@echo off
echo Запуск ProxiFyre Config Editor (exe версия)...
echo.
if exist "dist\ProxiFyreConfigEditor.exe" (
    start "" "dist\ProxiFyreConfigEditor.exe"
) else (
    echo Exe файл не найден! Сначала создайте его командой: python build_exe.py
    pause
)

