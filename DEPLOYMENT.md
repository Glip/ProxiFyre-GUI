# Инструкции по развертыванию

## Подготовка к первому запуску

### 1. Клонирование репозитория

```bash
git clone <your-repo-url>
cd ProxiFyre-gui
```

### 2. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 3. Проверка конфигурации

Убедитесь, что файл `app-config.json` существует и содержит корректную структуру. Если файл отсутствует, приложение создаст его автоматически при первом запуске.

## Сборка исполняемого файла

### Автоматическая сборка

```bash
python build_exe.py
```

Или используйте готовый bat файл:

```bash
build_exe.bat
```

### Ручная сборка

```bash
pyinstaller --onefile --windowed --name=ProxiFyreConfigEditor config_editor.py
```

## Структура файлов после сборки

После успешной сборки в папке `dist/` появится файл `ProxiFyreConfigEditor.exe`.

## Запуск приложения

### Python версия

```bash
python config_editor.py
```

Или используйте bat файл:

```bash
run_editor.bat
```

### Exe версия

```bash
run_exe.bat
```

Или запустите напрямую:

```bash
dist\ProxiFyreConfigEditor.exe
```

## Требования к системе

- Windows 10/11
- Python 3.7+ (для Python версии)
- Права администратора (для управления сервисом)

## Устранение неполадок

### Ошибка "ProxiFyre.exe не найден"

Убедитесь, что файл `ProxiFyre.exe` находится в той же папке, что и приложение.

### Ошибки при управлении сервисом

- Запустите приложение от имени администратора
- Убедитесь, что у вас есть права на управление службами Windows
- Проверьте, что ProxiFyre.exe поддерживает команды `install`, `start`, `stop`, `uninstall`

### Проблемы с PyInstaller

```bash
pip uninstall pyinstaller
pip install pyinstaller
```

## Обновление приложения

1. Получите последние изменения:
   ```bash
   git pull origin main
   ```

2. Установите обновленные зависимости:
   ```bash
   pip install -r requirements.txt
   ```

3. Пересоберите exe файл:
   ```bash
   python build_exe.py
   ```
