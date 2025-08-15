@echo off
echo Запуск ProxiFyre GUI by turn-guild.ru (exe версия)...
echo.
if exist "dist\ProxiFyreGUI.exe" (
    start "" "dist\ProxiFyreGUI.exe"
) else (
    echo Exe файл не найден! Сначала создайте его командой: python build_exe.py
    pause
)

