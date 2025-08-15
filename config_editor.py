import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
import subprocess
import psutil
from typing import List, Dict, Any
import urllib.request
import zipfile
import tempfile
import re
import shutil

class ConfigEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("ProxiFyre GUI by turn-guild.ru")
        self.root.geometry("800x600")
        
        self.config_file = "app-config.json"
        self.config_data = self.load_config()
        
        self.setup_ui()
        self.load_current_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Загружает конфигурацию из файла"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Создаем базовую структуру если файл не существует
                return {
                    "logLevel": "Error",
                    "proxies": [
                        {
                            "appNames": [],
                            "socks5ProxyEndpoint": "",
                            "username": "",
                            "password": "",
                            "supportedProtocols": ["TCP", "UDP"]
                        }
                    ]
                }
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить конфигурацию: {str(e)}")
            return {}
    
    def save_config(self):
        """Сохраняет конфигурацию в файл"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config_data, f, indent=1, ensure_ascii=False)
            messagebox.showinfo("Успех", "Конфигурация сохранена!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить конфигурацию: {str(e)}")
    
    def setup_ui(self):
        """Настраивает пользовательский интерфейс"""
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Настройки прокси
        proxy_frame = ttk.LabelFrame(main_frame, text="Настройки прокси", padding="10")
        proxy_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Endpoint
        ttk.Label(proxy_frame, text="Socks5 Proxy Endpoint:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.endpoint_var = tk.StringVar()
        ttk.Entry(proxy_frame, textvariable=self.endpoint_var, width=40).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        
        # Username
        ttk.Label(proxy_frame, text="Username:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.username_var = tk.StringVar()
        ttk.Entry(proxy_frame, textvariable=self.username_var, width=40).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        
        # Password
        ttk.Label(proxy_frame, text="Password:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.password_var = tk.StringVar()
        ttk.Entry(proxy_frame, textvariable=self.password_var, width=40, show="*").grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        
        # Log Level
        ttk.Label(proxy_frame, text="Log Level:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.log_level_var = tk.StringVar()
        log_level_combo = ttk.Combobox(proxy_frame, textvariable=self.log_level_var, values=["Error", "Warning", "Info", "Debug"], state="readonly", width=37)
        log_level_combo.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        
        # Приложения
        apps_frame = ttk.LabelFrame(main_frame, text="Приложения", padding="10")
        apps_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Список приложений
        self.apps_listbox = tk.Listbox(apps_frame, height=8, width=60)
        self.apps_listbox.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Кнопки для управления приложениями
        ttk.Button(apps_frame, text="Добавить приложение", command=self.add_app).grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        ttk.Button(apps_frame, text="Удалить приложение", command=self.remove_app).grid(row=1, column=1, sticky=tk.W)
        
        # Кнопки для управления приложением
        app_control_frame = ttk.LabelFrame(main_frame, text="Управление приложением", padding="10")
        app_control_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(app_control_frame, text="Запустить приложение", command=self.run_proxifyre).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(app_control_frame, text="Остановить приложение", command=self.stop_proxifyre).grid(row=0, column=1, padx=(0, 10))
        ttk.Button(app_control_frame, text="Скачать ProxiFyre", command=self.download_proxifyre).grid(row=0, column=2, padx=(0, 10))
        
        # Кнопки для управления сервисом (требуют права администратора)
        service_control_frame = ttk.LabelFrame(main_frame, text="Управление сервисом (требует права администратора)", padding="10")
        service_control_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(service_control_frame, text="Установить как сервис", command=self.install_service).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(service_control_frame, text="Запустить", command=self.start_service).grid(row=0, column=1, padx=(0, 10))
        ttk.Button(service_control_frame, text="Остановить", command=self.stop_service).grid(row=0, column=2, padx=(0, 10))
        ttk.Button(service_control_frame, text="Удалить сервис", command=self.uninstall_service).grid(row=0, column=3, padx=(0, 10))
        
        # Кнопки действий
        actions_frame = ttk.Frame(main_frame)
        actions_frame.grid(row=4, column=0, columnspan=2, pady=(10, 0))
        
        ttk.Button(actions_frame, text="Сохранить", command=self.save_config).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(actions_frame, text="Обновить", command=self.load_current_config).grid(row=0, column=1, padx=(0, 10))
        ttk.Button(actions_frame, text="Выход", command=self.root.quit).grid(row=0, column=2)
        
        # Настройка весов для растягивания
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        apps_frame.columnconfigure(0, weight=1)
        apps_frame.rowconfigure(0, weight=1)
        app_control_frame.columnconfigure(2, weight=1)
    
    def load_current_config(self):
        """Загружает текущую конфигурацию в интерфейс"""
        if not self.config_data or "proxies" not in self.config_data or not self.config_data["proxies"]:
            return
        
        proxy = self.config_data["proxies"][0]
        
        # Загружаем настройки прокси
        self.endpoint_var.set(proxy.get("socks5ProxyEndpoint", ""))
        self.username_var.set(proxy.get("username", ""))
        self.password_var.set(proxy.get("password", ""))
        self.log_level_var.set(self.config_data.get("logLevel", "Error"))
        
        # Загружаем список приложений
        self.apps_listbox.delete(0, tk.END)
        for app in proxy.get("appNames", []):
            self.apps_listbox.insert(tk.END, app)
    
    def add_app(self):
        """Добавляет новое приложение через диалог выбора файла"""
        file_path = filedialog.askopenfilename(
            title="Выберите приложение",
            filetypes=[
                ("Executable files", "*.exe;*.bat"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            app_name = os.path.basename(file_path)
            if app_name not in self.get_current_apps():
                self.apps_listbox.insert(tk.END, app_name)
                self.update_config_from_ui()
            else:
                messagebox.showwarning("Предупреждение", "Это приложение уже добавлено в список!")
    
    def remove_app(self):
        """Удаляет выбранное приложение из списка"""
        selection = self.apps_listbox.curselection()
        if selection:
            self.apps_listbox.delete(selection)
            self.update_config_from_ui()
        else:
            messagebox.showwarning("Предупреждение", "Выберите приложение для удаления!")
    
    def get_current_apps(self) -> List[str]:
        """Получает текущий список приложений из интерфейса"""
        apps = []
        for i in range(self.apps_listbox.size()):
            apps.append(self.apps_listbox.get(i))
        return apps
    
    def update_config_from_ui(self):
        """Обновляет конфигурацию на основе данных из интерфейса"""
        if not self.config_data:
            self.config_data = {
                "logLevel": "Error",
                "proxies": [
                    {
                        "appNames": [],
                        "socks5ProxyEndpoint": "",
                        "username": "",
                        "password": "",
                        "supportedProtocols": ["TCP", "UDP"]
                    }
                ]
            }
        
        # Обновляем настройки прокси
        self.config_data["logLevel"] = self.log_level_var.get()
        
        if not self.config_data["proxies"]:
            self.config_data["proxies"] = [{}]
        
        proxy = self.config_data["proxies"][0]
        proxy["socks5ProxyEndpoint"] = self.endpoint_var.get()
        proxy["username"] = self.username_var.get()
        proxy["password"] = self.password_var.get()
        proxy["appNames"] = self.get_current_apps()
        
        # Сохраняем поддерживаемые протоколы если их нет
        if "supportedProtocols" not in proxy:
            proxy["supportedProtocols"] = ["TCP", "UDP"]
    
    def download_proxifyre(self):
        """Скачивает последний релиз ProxiFyre с GitHub"""
        try:
            # Используем GitHub API для получения информации о последнем релизе
            api_url = "https://api.github.com/repos/wiresock/proxifyre/releases/latest"
            req = urllib.request.Request(api_url, headers={
                'User-Agent': 'Mozilla/5.0',
                'Accept': 'application/vnd.github.v3+json'
            })
            
            with urllib.request.urlopen(req) as response:
                release_data = json.loads(response.read().decode('utf-8'))
            
            # Ищем ссылку на архив в assets
            zip_url = None
            for asset in release_data.get('assets', []):
                asset_name = asset.get('name', '')
                if any(pattern in asset_name.lower() for pattern in ['x64-signed.zip', 'x86-signed.zip']):
                    zip_url = asset.get('browser_download_url')
                    break
            
            if not zip_url:
                messagebox.showerror("Ошибка", f"Не удалось найти архив в релизе {release_data.get('tag_name', 'unknown')}")
                return
            
            # Создаем временную папку для загрузки
            with tempfile.TemporaryDirectory() as temp_dir:
                zip_path = os.path.join(temp_dir, "proxifyre.zip")
                
                # Скачиваем архив
                urllib.request.urlretrieve(zip_url, zip_path)
                
                # Разархивируем все файлы в текущую папку
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(".")
                
                # Проверяем, что файлы извлечены
                extracted_files = []
                for root, dirs, files in os.walk("."):
                    for file in files:
                        if file.endswith('.exe') or file.endswith('.dll') or file.endswith('.txt') or file.endswith('.md'):
                            extracted_files.append(file)
                
                if extracted_files:
                    messagebox.showinfo("Успех", f"Архив успешно распакован! Извлечено файлов: {len(extracted_files)}")
                else:
                    messagebox.showerror("Ошибка", "Не удалось распаковать архив")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось скачать ProxiFyre: {str(e)}")
    
    def run_proxifyre(self):
        """Запускает приложение ProxiFyre.exe"""
        try:
            if os.path.exists("ProxiFyre.exe"):
                subprocess.Popen(["ProxiFyre.exe"], creationflags=subprocess.CREATE_NEW_CONSOLE)
                messagebox.showinfo("Успех", "ProxiFyre запущен!")
            else:
                messagebox.showerror("Ошибка", "Файл ProxiFyre.exe не найден в текущей папке!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось запустить ProxiFyre: {str(e)}")
    
    def stop_proxifyre(self):
        """Останавливает приложение ProxiFyre.exe"""
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] == 'ProxiFyre.exe':
                    proc.terminate()
                    messagebox.showinfo("Успех", "ProxiFyre остановлен!")
                    return
            
            messagebox.showinfo("Информация", "ProxiFyre не запущен")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось остановить ProxiFyre: {str(e)}")
    
    def install_service(self):
        """Устанавливает ProxiFyre как сервис"""
        try:
            if os.path.exists("ProxiFyre.exe"):
                result = subprocess.run(["ProxiFyre.exe", "install"], 
                                      capture_output=True, text=True, 
                                      creationflags=subprocess.CREATE_NO_WINDOW)
                if result.returncode == 0:
                    messagebox.showinfo("Успех", "Сервис ProxiFyre установлен!")
                else:
                    messagebox.showerror("Ошибка", f"Не удалось установить сервис: {result.stderr}")
            else:
                messagebox.showerror("Ошибка", "Файл ProxiFyre.exe не найден в текущей папке!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось установить сервис: {str(e)}")
    
    def start_service(self):
        """Запускает сервис ProxiFyre"""
        try:
            if os.path.exists("ProxiFyre.exe"):
                result = subprocess.run(["ProxiFyre.exe", "start"], 
                                      capture_output=True, text=True, 
                                      creationflags=subprocess.CREATE_NO_WINDOW)
                if result.returncode == 0:
                    messagebox.showinfo("Успех", "Сервис ProxiFyre запущен!")
                else:
                    messagebox.showerror("Ошибка", f"Не удалось запустить сервис: {result.stderr}")
            else:
                messagebox.showerror("Ошибка", "Файл ProxiFyre.exe не найден в текущей папке!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось запустить сервис: {str(e)}")
    
    def stop_service(self):
        """Останавливает сервис ProxiFyre"""
        try:
            if os.path.exists("ProxiFyre.exe"):
                result = subprocess.run(["ProxiFyre.exe", "stop"], 
                                      capture_output=True, text=True, 
                                      creationflags=subprocess.CREATE_NO_WINDOW)
                if result.returncode == 0:
                    messagebox.showinfo("Успех", "Сервис ProxiFyre остановлен!")
                else:
                    messagebox.showerror("Ошибка", f"Не удалось остановить сервис: {result.stderr}")
            else:
                messagebox.showerror("Ошибка", "Файл ProxiFyre.exe не найден в текущей папке!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось остановить сервис: {str(e)}")
    
    def uninstall_service(self):
        """Удаляет сервис ProxiFyre"""
        try:
            if os.path.exists("ProxiFyre.exe"):
                result = subprocess.run(["ProxiFyre.exe", "uninstall"], 
                                      capture_output=True, text=True, 
                                      creationflags=subprocess.CREATE_NO_WINDOW)
                if result.returncode == 0:
                    messagebox.showinfo("Успех", "Сервис ProxiFyre удален!")
                else:
                    messagebox.showerror("Ошибка", f"Не удалось удалить сервис: {result.stderr}")
            else:
                messagebox.showerror("Ошибка", "Файл ProxiFyre.exe не найден в текущей папке!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось удалить сервис: {str(e)}")

def main():
    root = tk.Tk()
    app = ConfigEditor(root)
    root.mainloop()

if __name__ == "__main__":
    main()
