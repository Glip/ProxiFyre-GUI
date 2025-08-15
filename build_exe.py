import subprocess
import sys
import os

def build_exe():
    """Упаковывает приложение в exe файл"""
    try:
        print("Начинаю упаковку приложения в exe...")
        
        # Команда для PyInstaller
        cmd = [
            "pyinstaller",
            "--onefile",  # Создать один exe файл
            "--windowed",  # Без консольного окна
            "--name=ProxiFyreGUI",  # Имя выходного файла
            "--icon=NONE",  # Без иконки (можно добавить свою)
            "config_editor.py"
        ]
        
        # Выполняем команду
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Приложение успешно упаковано!")
            print(f"📁 Exe файл находится в папке: dist/ProxiFyreGUI.exe")
            print(f"📁 Временные файлы в папке: build/")
        else:
            print("❌ Ошибка при упаковке:")
            print(result.stderr)
            
    except FileNotFoundError:
        print("❌ PyInstaller не найден. Установите его командой:")
        print("pip install pyinstaller")
    except Exception as e:
        print(f"❌ Произошла ошибка: {str(e)}")

if __name__ == "__main__":
    build_exe()
