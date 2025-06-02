import sys
import traceback
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QCheckBox, QFrame, QPushButton, QLineEdit, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QFont, QIcon, QAction
from PyQt6.QtCore import QTimer, Qt
import psutil, GPUtil, threading, requests, asyncio
from weather import get_weather, icons
from telegram_bot import TelegramBot
import json

def log_error(e):
    with open("error.log", "a", encoding="utf-8") as f:
        f.write(str(e) + "\n")
        traceback.print_exc(file=f)

# --- Вынесите config сюда ---
config = {
    'AK_weather': "",
    'AK_telegram': "",
    'city': "",
    'bot_bool': False
}
# ----------------------------

def create_config():
    try:
        with open('config.json', 'w', encoding='utf-8') as file:
            json.dump(config, file, indent=4)
        return True
    except Exception as e:
        print(f"Error creating config: {e}")
        return False

def load_config():
    global config
    try:
        with open('config.json', 'r', encoding='utf-8') as file:
            config.update(json.load(file))
        return True
    except FileNotFoundError:
        print("Config file not found")
        create_config()
        return False
    except Exception as e:
        print(f"Error loading config: {e}")
        return False

class SettingsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Настройки")
        self.setGeometry(100, 100, 100, 200)
        self.settings_window = None  
    
    
        # Telegram-бот
        self.telegram_bot = None
        self.bot_thread = None

        self.initUI()
        self.update_weather()
        self.update_stats()

        #Таймерики, сверху для статистики, снизу для погоды
        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self.update_stats)
        self.stats_timer.start(1000)  

        self.weather_timer = QTimer()
        self.weather_timer.timeout.connect(self.update_weather)
        self.weather_timer.start(600000)  


    def initUI(self):
        main_layout = QVBoxLayout()  # Changed to QVBoxLayout to stack vertically
        # Кнопка настроек
        settings_btn = QPushButton("⚙️ Настройки")
        settings_btn.setFont(QFont("Arial", 12))
        settings_btn.clicked.connect(self.open_settings)
        main_layout.addWidget(settings_btn)

        # Основной контент
        content_layout = QHBoxLayout()

        # Левая часть (бот и погода)
        left_layout = QVBoxLayout()
        
        # Статус бота из конфига
        self.bot_status = QLabel("Бот включен" if config.get('bot_bool', False) else "Бот выключен")
        self.bot_status.setFont(QFont("Arial", 16))
        left_layout.addWidget(self.bot_status)

        # Горизонтальный layout для города и обновления
        city_layout = QHBoxLayout()

        # Название города
        self.city_label = QLabel(f"{config.get('city', 'не указан')}")
        self.city_label.setFont(QFont("Arial", 16))
        self.city_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        city_layout.addWidget(self.city_label)
        
        # Кнопка обновления
        refresh_btn = QPushButton("🔄")
        refresh_btn.setFixedSize(30, 30)
        refresh_btn.setFont(QFont("Arial", 10))
        refresh_btn.clicked.connect(self.refresh_data)
        city_layout.addWidget(refresh_btn)

        left_layout.addLayout(city_layout)

        # Иконка погоды и температура
        self.weather_label = QLabel()
        self.weather_label.setFont(QFont("Arial", 24))
        left_layout.addWidget(self.weather_label)

        # Описание погоды
        self.weather_desc = QLabel()
        self.weather_desc.setFont(QFont("Arial", 16))
        left_layout.addWidget(self.weather_desc)

        # "Ощущается как"
        self.feels_like_label = QLabel()
        self.feels_like_label.setFont(QFont("Arial", 16))
        left_layout.addWidget(self.feels_like_label)

        content_layout.addLayout(left_layout)

        # Разделительная линия с отступами
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setContentsMargins(5, 0, 5, 0)
        content_layout.addWidget(separator)

        #системные ресурсы
        right_layout = QVBoxLayout()
        self.cpu_label = QLabel("CPU: ...%")
        self.gpu_label = QLabel("GPU: ...%")
        self.ram_label = QLabel("RAM: ...%")

        for lbl in [self.cpu_label, self.gpu_label, self.ram_label]:
            lbl.setFont(QFont("Arial", 16))
            right_layout.addWidget(lbl)

        self.tray_icon = QSystemTrayIcon(QIcon("icon.ico"), self)
        self.tray_icon.setToolTip("PC Helper")
        self.tray_icon.activated.connect(self.on_tray_activated)

        tray_menu = QMenu()
        restore_action = QAction("Показать", self)
        restore_action.triggered.connect(self.showNormal)
        quit_action = QAction("Выход", self)
        quit_action.triggered.connect(QApplication.instance().quit)
        tray_menu.addAction(restore_action)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()


        content_layout.addLayout(right_layout)
        main_layout.addLayout(content_layout)
        self.setLayout(main_layout)

    def open_settings(self):
        if self.settings_window is None:
            self.settings_window = QWidget()
            self.settings_window.setWindowTitle("Настройки программы")
            self.settings_window.setGeometry(200, 200, 300, 350)

            layout = QVBoxLayout()

            # Telegram Bot Section Header
            tg_header = QLabel("Настройки Telegram бота")
            tg_header.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            layout.addWidget(tg_header)
            layout.setSpacing(5)  # Уменьшаем отступы между элементами

            # Telegram bot checkbox
            self.tg_bot_checkbox = QCheckBox("Telegram бот")
            self.tg_bot_checkbox.setChecked(config.get('bot_bool', False))
            layout.addWidget(self.tg_bot_checkbox)

            # Token input field with current token
            self.token_input = QLineEdit()
            self.token_input.setPlaceholderText("Введите токен Telegram бота")
            current_token = config.get('AK_telegram', '')
            self.token_input.setText(current_token)
            layout.addWidget(self.token_input)

            # Weather Section Header
            weather_header = QLabel("Настройки погоды")
            weather_header.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            layout.addWidget(weather_header)

            # Weather API key input
            self.weather_api_input = QLineEdit()
            self.weather_api_input.setPlaceholderText("Введите API ключ погоды")
            current_weather_api = config.get('AK_weather', '')
            self.weather_api_input.setText(current_weather_api)
            layout.addWidget(self.weather_api_input)

            # City input
            self.city_input = QLineEdit()
            self.city_input.setPlaceholderText("Введите название города")
            current_city = config.get('city', '')
            self.city_input.setText(current_city)
            layout.addWidget(self.city_input)

            # Это мы тоже убираем
            #self.dpi_checkbox = QCheckBox("Включить защиту от DPI")
            #self.dpi_checkbox.setChecked(config.get('dpi_enabled', False))
            #layout.addWidget(self.dpi_checkbox)

            # Apply button
            apply_btn = QPushButton("Применить")
            apply_btn.clicked.connect(self.apply_settings)
            layout.addWidget(apply_btn)

            self.settings_window.setLayout(layout)
        self.settings_window.show()


    def apply_settings(self):
        token = self.token_input.text().strip()
        weather_api = self.weather_api_input.text().strip()
        city = self.city_input.text().strip()

        # Обновляем значения в config
        config['AK_telegram'] = token
        config['AK_weather'] = weather_api
        config['city'] = city
        config['bot_bool'] = self.tg_bot_checkbox.isChecked()

        # Сохраняем в config.json
        try:
            with open('config.json', 'w', encoding='utf-8') as file:
                json.dump(config, file, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Ошибка сохранения настроек: {e}")

        # Перезагружаем config и обновляем интерфейс
        load_config()
        self.refresh_data()

        print("Settings updated successfully")
        self.settings_window.close()

        # Эта часть кода закомментирована, так как она не используется
        #dpi_enabled = self.dpi_checkbox.isChecked()
        #updated = False
        #for i, line in enumerate(content):
        #    if line.startswith('dpi_enabled='):
        #        content[i] = f'dpi_enabled={dpi_enabled}\n'
        #        updated = True
        #if not updated:
        #    content.append(f'dpi_enabled={dpi_enabled}\n')

        # Write updated content back to the file
        # Если токен изменился, предупреждаем пользователя о необходимости перезапуска

    

    def start_telegram_bot(self):
        if not self.telegram_bot:
            token = config.get('AK_telegram', '')
            if not token:
                print("Токен Telegram-бота не указан")
                self.bot_status.setText("Ошибка TG-бота T1")
                return
            # Проверяем токен и получаем my_id
            url = f"https://api.telegram.org/bot{token}/getMe"
            try:
                response = requests.get(url)
                if response.status_code != 200 or not response.json().get("ok"):
                    raise ValueError("Недействительный токен Telegram-бота")
            except Exception as e:
                print(f"Ошибка проверки токена: {e}")
                self.bot_status.setText("Ошибка TG-бота T2")
                return

            # Создаем и запускаем Telegram-бота
            try:
                self.telegram_bot = TelegramBot(token, config.get('AK_telegram_id', ''))  # Передаем my_id
                self.bot_thread = threading.Thread(target=self.telegram_bot.start_bot, daemon=True)
                self.bot_thread.start()
                print("Telegram-бот запущен")
                self.bot_status.setText("TG-бот работает")
            except Exception as e:
                print(f"Error starting telegram bot: {e}")
                self.bot_status.setText("Ошибка TG-бота E0")



    def stop_telegram_bot(self):
        if self.telegram_bot:
            try:
                self.telegram_bot.stop_bot()  # Асинхронный вызов
                self.telegram_bot = None
                self.bot_thread = None
                print("Telegram-бот остановлен")
                self.bot_status.setText("TG-бота отключен")
            except Exception as e:
                print(f"Ошибка остановки Telegram-бота: {e}")

    def refresh_data(self):
        load_config()
        city = config.get('city', 'не указан')
        self.city_label.setText(f"{city}")
    
        # Обновляем данные погоды
        self.update_weather()

    
        print("Данные обновлены")

    def update_weather(self):
        try:
            city = config.get('city', 'не указан')
            weather = get_weather(city, config.get('AK_weather', ''))
            if weather and all(weather.values()):
                icon = icons.get(weather['icon'], '❓') # ля какая иконка 
                self.weather_label.setText(f"{icon}  {weather['temperature']}°C")
                self.weather_desc.setText(f"{weather['description']}".capitalize())
                self.feels_like_label.setText(f"Ощущается как: {weather['temperature_feels']}°C")
            else:
                self.weather_label.setText("❌ Нет данных") # и здесь тоже
                self.weather_desc.setText(f"Погода: --")
                self.feels_like_label.setText(f"Ощущается как: --°C")
        except Exception as e:
            self.weather_label.setText("❌ Ошибка") # А тут другая 
            self.weather_desc.setText(f"Погода: --")
            self.feels_like_label.setText(f"Ощущается как: --°C")
            print(f"Weather update error: {e}")

    def update_stats(self):
        # Тут у нас CPU, RAM и GPU
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        gpus = GPUtil.getGPUs() # GPU
        gpu = gpus[0].load * 100  # Процентики
        #Обновляем
        self.gpu_label.setText(f"GPU: {gpu:.1f}%")
        self.cpu_label.setText(f"CPU: {cpu}%")
        self.ram_label.setText(f"RAM: {ram}%")

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.tray_icon.showMessage("PC Helper", "Приложение свернуто в трей", QSystemTrayIcon.MessageIcon.Information)

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.showNormal()
            self.activateWindow()

if __name__ == "__main__":
    try:
        if not load_config():
            create_config()
        app = QApplication(sys.argv)
        app.setWindowIcon(QIcon("icon.ico"))  
        window = SettingsWindow()
        window.start_telegram_bot()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        log_error(e)


