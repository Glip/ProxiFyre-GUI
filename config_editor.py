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
        self.root.geometry("1000x800")
        
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
        """Настраивает пользовательский интерфейс с вкладками"""
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Создаем вкладки
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Вкладка "Основное"
        main_tab = ttk.Frame(notebook, padding="10")
        notebook.add(main_tab, text="Основное")
        self._setup_main_tab(main_tab)
        
        # Вкладка "Сервис"
        service_tab = ttk.Frame(notebook, padding="10")
        notebook.add(service_tab, text="Сервис")
        self._setup_service_tab(service_tab)
        
        # Кнопки действий (общие для всех вкладок)
        actions_frame = ttk.Frame(main_frame)
        actions_frame.grid(row=1, column=0, pady=(10, 0))
        
        ttk.Button(actions_frame, text="Сохранить", command=self.save_config).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(actions_frame, text="Обновить", command=self.load_current_config).grid(row=0, column=1, padx=(0, 10))
        ttk.Button(actions_frame, text="Выход", command=self.root.quit).grid(row=0, column=2)
        
        # Настройка весов для растягивания
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
    
    def _setup_main_tab(self, parent):
        """Настраивает вкладку 'Основное'"""
        # Настройки прокси
        proxy_frame = ttk.LabelFrame(parent, text="Настройки прокси", padding="10")
        proxy_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Endpoint
        ttk.Label(proxy_frame, text="Socks5 Proxy Endpoint:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.endpoint_var = tk.StringVar()
        
        # Username
        ttk.Label(proxy_frame, text="Username:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.username_var = tk.StringVar()
        
        # Password
        ttk.Label(proxy_frame, text="Password:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.password_var = tk.StringVar()
        
        # Log Level
        ttk.Label(proxy_frame, text="Log Level:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.log_level_var = tk.StringVar()
        log_level_combo = ttk.Combobox(proxy_frame, textvariable=self.log_level_var, values=["Error", "Warning", "Info", "Debug"], state="readonly", width=37)
        log_level_combo.grid(row=3, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        
        # Приложения
        apps_frame = ttk.LabelFrame(parent, text="Приложения", padding="10")
        apps_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Список приложений
        self.apps_listbox = tk.Listbox(apps_frame, height=8, width=60)
        self.apps_listbox.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Кнопки для управления приложениями
        ttk.Button(apps_frame, text="Добавить приложение", command=self.add_app).grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        ttk.Button(apps_frame, text="Удалить приложение", command=self.remove_app).grid(row=1, column=1, sticky=tk.W)
        
        # Кнопки для управления приложением
        app_control_frame = ttk.LabelFrame(parent, text="Управление приложением", padding="10")
        app_control_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(app_control_frame, text="Запустить приложение", command=self.run_proxifyre).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(app_control_frame, text="Остановить приложение", command=self.stop_proxifyre).grid(row=0, column=1, padx=(0, 10))
        ttk.Button(app_control_frame, text="Скачать ProxiFyre", command=self.download_proxifyre).grid(row=0, column=2, padx=(0, 10))
        
        # Встроенная консоль
        console_frame = ttk.LabelFrame(parent, text="Консоль ProxiFyre", padding="10")
        console_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Консоль с прокруткой
        self.console_text = tk.Text(console_frame, height=12, width=80, bg='black', fg='white', font=('Consolas', 9))
        console_scrollbar = ttk.Scrollbar(console_frame, orient="vertical", command=self.console_text.yview)
        self.console_text.configure(yscrollcommand=console_scrollbar.set)
        
        self.console_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        console_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Кнопки управления консолью
        console_buttons_frame = ttk.Frame(console_frame)
        console_buttons_frame.grid(row=1, column=0, columnspan=2, pady=(10, 0))
        
        ttk.Button(console_buttons_frame, text="Очистить консоль", command=self.clear_console).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(console_buttons_frame, text="Копировать вывод", command=self.copy_console_output).grid(row=0, column=1, padx=(0, 10))
        
        # Настройка весов для растягивания
        parent.columnconfigure(1, weight=1)
        apps_frame.columnconfigure(0, weight=1)
        apps_frame.rowconfigure(0, weight=1)
        app_control_frame.columnconfigure(2, weight=1)
        console_frame.columnconfigure(0, weight=1)
        console_frame.rowconfigure(0, weight=1)
        
        # Создаем поля ввода с контекстным меню
        self._create_entry_fields(proxy_frame)
    
    def _setup_service_tab(self, parent):
        """Настраивает вкладку 'Сервис'"""
        # Информация о сервисе
        info_frame = ttk.LabelFrame(parent, text="Информация о сервисе", padding="10")
        info_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        ttk.Label(info_frame, text="Эта вкладка содержит функции для управления ProxiFyre как системным сервисом Windows.").grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=5)
        ttk.Label(info_frame, text="Все операции требуют прав администратора.", foreground="red").grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Кнопки для управления сервисом
        service_control_frame = ttk.LabelFrame(parent, text="Управление сервисом", padding="10")
        service_control_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Первый ряд кнопок
        ttk.Button(service_control_frame, text="Установить как сервис", command=self.install_service).grid(row=0, column=0, padx=(0, 10), pady=(0, 10))
        ttk.Button(service_control_frame, text="Удалить сервис", command=self.uninstall_service).grid(row=0, column=1, padx=(0, 10), pady=(0, 10))
        
        # Второй ряд кнопок
        ttk.Button(service_control_frame, text="Запустить сервис", command=self.start_service).grid(row=1, column=0, padx=(0, 10))
        ttk.Button(service_control_frame, text="Остановить сервис", command=self.stop_service).grid(row=1, column=1, padx=(0, 10))
        
        # Статус сервиса
        status_frame = ttk.LabelFrame(parent, text="Статус сервиса", padding="10")
        status_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        self.service_status_label = ttk.Label(status_frame, text="Статус: Неизвестно")
        self.service_status_label.grid(row=0, column=0, sticky=tk.W, pady=5)
        
        ttk.Button(status_frame, text="Обновить статус", command=self.refresh_service_status).grid(row=1, column=0, sticky=tk.W, pady=5)
        
        # Настройка весов
        parent.columnconfigure(1, weight=1)
        service_control_frame.columnconfigure(1, weight=1)
    
    def _create_entry_fields(self, proxy_frame):
        """Создает поля ввода с контекстным меню для копирования/вставки"""
        # Endpoint
        self.endpoint_entry = ttk.Entry(proxy_frame, textvariable=self.endpoint_var, width=40)
        self.endpoint_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        self._setup_entry_context_menu(self.endpoint_entry)
        
        # Username
        self.username_entry = ttk.Entry(proxy_frame, textvariable=self.username_var, width=40)
        self.username_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        self._setup_entry_context_menu(self.username_entry)
        
        # Password
        self.password_entry = ttk.Entry(proxy_frame, textvariable=self.password_var, width=40, show="*")
        self.password_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        self._setup_entry_context_menu(self.password_entry)
    
    def _setup_entry_context_menu(self, entry_widget):
        """Настраивает контекстное меню для поля ввода"""
        context_menu = tk.Menu(entry_widget, tearoff=0)
        context_menu.add_command(label="Копировать (Ctrl+C/С)", command=lambda: self._copy_text(entry_widget))
        context_menu.add_command(label="Вставить (Ctrl+V/М)", command=lambda: self._paste_text(entry_widget))
        context_menu.add_command(label="Вырезать (Ctrl+X/Ч)", command=lambda: self._cut_text(entry_widget))
        context_menu.add_separator()
        context_menu.add_command(label="Выбрать все (Ctrl+A/Ф)", command=lambda: self._select_all(entry_widget))
        
        # Привязываем правый клик к контекстному меню
        entry_widget.bind("<Button-3>", lambda e: context_menu.post(e.x_root, e.y_root))
        
        # Привязываем горячие клавиши (работают независимо от раскладки)
        entry_widget.bind("<Control-Insert>", lambda e: self._copy_text(entry_widget))  # Ctrl+Insert
        entry_widget.bind("<Shift-Insert>", lambda e: self._paste_text(entry_widget))   # Shift+Insert
        entry_widget.bind("<Shift-Delete>", lambda e: self._cut_text(entry_widget))    # Shift+Delete
        entry_widget.bind("<Control-a>", lambda e: self._select_all(entry_widget))     # Ctrl+A
        entry_widget.bind("<Control-A>", lambda e: self._select_all(entry_widget))     # Ctrl+A (Shift)
        
        # Альтернативные горячие клавиши (работают при любой раскладке)
        # Используем KeyPress для перехвата нажатий клавиш
        entry_widget.bind("<KeyPress>", self._handle_key_press)
    
    def _handle_key_press(self, event):
        """Обрабатывает нажатия клавиш для альтернативных горячих клавиш"""
        # Проверяем, что нажат Ctrl
        if event.state & 0x4:  # 0x4 = Control
            # Используем keycode для определения клавиши (работает независимо от раскладки)
            keycode = event.keycode
            
            # Определяем действие по коду клавиши
            if keycode == 67:  # Клавиша C (английская) или С (русская)
                self._copy_text(event.widget)
                return "break"  # Предотвращаем стандартную обработку
            elif keycode == 86:  # Клавиша V (английская) или М (русская)
                self._paste_text(event.widget)
                return "break"
            elif keycode == 88:  # Клавиша X (английская) или Ч (русская)
                self._cut_text(event.widget)
                return "break"
            elif keycode == 65:  # Клавиша A (английская) или Ф (русская)
                self._select_all(event.widget)
                return "break"
    
    def _copy_text(self, entry_widget):
        """Копирует выделенный текст"""
        try:
            selected_text = entry_widget.selection_get()
            self.root.clipboard_clear()
            self.root.clipboard_append(selected_text)
        except tk.TclError:
            pass  # Нет выделенного текста
    
    def _paste_text(self, entry_widget):
        """Вставляет текст из буфера обмена"""
        try:
            clipboard_text = self.root.clipboard_get()
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, clipboard_text)
        except tk.TclError:
            pass  # Буфер обмена пуст
    
    def _cut_text(self, entry_widget):
        """Вырезает выделенный текст"""
        try:
            selected_text = entry_widget.selection_get()
            self.root.clipboard_clear()
            self.root.clipboard_append(selected_text)
            entry_widget.delete("sel.first", "sel.last")
        except tk.TclError:
            pass  # Нет выделенного текста
    
    def _select_all(self, entry_widget):
        """Выбирает весь текст в поле"""
        entry_widget.select_range(0, tk.END)
        entry_widget.icursor(tk.END)
    
    def refresh_service_status(self):
        """Обновляет статус сервиса"""
        try:
            # Проверяем статус сервиса через sc query
            result = subprocess.run(["sc", "query", "ProxiFyre"], 
                                  capture_output=True, text=True, 
                                  creationflags=subprocess.CREATE_NO_WINDOW)
            
            if result.returncode == 0:
                if "RUNNING" in result.stdout:
                    self.service_status_label.config(text="Статус: Запущен", foreground="green")
                elif "STOPPED" in result.stdout:
                    self.service_status_label.config(text="Статус: Остановлен", foreground="red")
                else:
                    self.service_status_label.config(text="Статус: Неизвестно", foreground="orange")
            else:
                self.service_status_label.config(text="Статус: Сервис не найден", foreground="gray")
        except Exception as e:
            self.service_status_label.config(text=f"Статус: Ошибка - {str(e)}", foreground="red")
    
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
        """Запускает приложение ProxiFyre.exe во встроенной консоли"""
        try:
            if os.path.exists("ProxiFyre.exe"):
                # Очищаем консоль перед запуском
                self.clear_console()
                self.log_to_console("🚀 Запуск ProxiFyre...\n")
                
                # Запускаем процесс без отдельного окна
                self.proxifyre_process = subprocess.Popen(
                    ["ProxiFyre.exe"], 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    universal_newlines=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                
                # Запускаем поток для чтения вывода
                import threading
                self.output_thread = threading.Thread(target=self._read_process_output, daemon=True)
                self.output_thread.start()
                
                self.log_to_console("✅ ProxiFyre запущен во встроенной консоли!\n")
            else:
                self.log_to_console("❌ Ошибка: Файл ProxiFyre.exe не найден в текущей папке!\n")
        except Exception as e:
            self.log_to_console(f"❌ Ошибка запуска: {str(e)}\n")
    
    def _read_process_output(self):
        """Читает вывод процесса и отображает в консоли"""
        try:
            while self.proxifyre_process and self.proxifyre_process.poll() is None:
                line = self.proxifyre_process.stdout.readline()
                if line:
                    self.log_to_console(line)
                else:
                    break
        except Exception as e:
            self.log_to_console(f"❌ Ошибка чтения вывода: {str(e)}\n")
    
    def log_to_console(self, message):
        """Добавляет сообщение в консоль"""
        try:
            self.console_text.insert(tk.END, message)
            self.console_text.see(tk.END)  # Прокручиваем к концу
            self.root.update_idletasks()  # Обновляем GUI
        except Exception as e:
            print(f"Ошибка записи в консоль: {e}")
    
    def clear_console(self):
        """Очищает консоль"""
        self.console_text.delete(1.0, tk.END)
    
    def copy_console_output(self):
        """Копирует содержимое консоли в буфер обмена"""
        try:
            content = self.console_text.get(1.0, tk.END)
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
            messagebox.showinfo("Успех", "Содержимое консоли скопировано в буфер обмена!")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось скопировать: {str(e)}")
    
    def stop_proxifyre(self):
        """Останавливает приложение ProxiFyre.exe"""
        try:
            if hasattr(self, 'proxifyre_process') and self.proxifyre_process:
                if self.proxifyre_process.poll() is None:  # Процесс еще запущен
                    self.proxifyre_process.terminate()
                    self.log_to_console("🛑 ProxiFyre остановлен!\n")
                else:
                    self.log_to_console("ℹ️ ProxiFyre уже не запущен\n")
            else:
                # Пытаемся найти и остановить процесс через psutil
                for proc in psutil.process_iter(['pid', 'name']):
                    if proc.info['name'] == 'ProxiFyre.exe':
                        proc.terminate()
                        self.log_to_console("🛑 ProxiFyre остановлен через psutil!\n")
                        return
                
                self.log_to_console("ℹ️ ProxiFyre не запущен\n")
        except Exception as e:
            self.log_to_console(f"❌ Ошибка остановки: {str(e)}\n")
    
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
