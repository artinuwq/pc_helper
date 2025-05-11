import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QCheckBox, QFrame, QPushButton, QLineEdit
from PyQt6.QtGui import QFont
from PyQt6.QtCore import QTimer, Qt
import psutil,GPUtil,threading,requests, asyncio

from weather import get_weather, icons  # Импортируем функцию получения погоды
from telegram_bot import TelegramBot


from weather import get_weather, icons  # 

# Пуской конфиг файл 
config = {
    'AK_weather': "",
    'AK_telegram': "",
    'city': "",
    'bot_bool': False
}

def create_config():
    default_config = '''AK_weather=""
                        AK_telegram=""
                        city=""
                        bot_bool=False'''
    try:
        with open('config.py', 'w', encoding='utf-8') as file:
            file.write(default_config)
        return True
    except Exception as e:
        print(f"Error creating config: {e}")
        return False

def load_config(): # о а это у нас загрузка конфига как не ожиданно
    try:
        with open('config.py', 'r', encoding='utf-8') as file:
            exec(file.read(), config)
        return True
    except FileNotFoundError:
        print("Config file not found")
        create_config()  # Create default config if not found
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
        config_path = 'config.py'
    
        # Read existing content
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                content = file.readlines()
        except FileNotFoundError:
            content = []

        if token != config.get('AK_telegram', ''):
            self.bot_status.setText("Требуется перезапуск")

        # Update or add token
        updated = False
        for i, line in enumerate(content):
            if line.startswith('AK_telegram='):
                content[i] = f'AK_telegram="{token}"\n'
                updated = True
        if not updated and token:
            content.append(f'AK_telegram="{token}"\n')
    
        # Update or add weather API key
        updated = False
        for i, line in enumerate(content):
            if line.startswith('AK_weather='):
                content[i] = f'AK_weather="{weather_api}"\n'
                updated = True
        if not updated and weather_api:
            content.append(f'AK_weather="{weather_api}"\n')
    
        # Update or add city
        updated = False
        for i, line in enumerate(content):
            if line.startswith('city='):
                content[i] = f'city="{city}"\n'
                updated = True
        if not updated and city:
            content.append(f'city="{city}"\n')
    
        # Update or add bot status
        bot_state = self.tg_bot_checkbox.isChecked()
        updated = False
        for i, line in enumerate(content):
            if line.startswith('bot_bool='):
                content[i] = f'bot_bool={bot_state}\n'
                updated = True
        if not updated:
            content.append(f'bot_bool={bot_state}\n')
    
        # Write updated content back to the file
        with open(config_path, 'w', encoding='utf-8') as file:
            file.writelines(content)
    
        # Reload the config to update the dictionary
        load_config()
    
        # Refresh the UI with updated data
        self.refresh_data()

        print("Settings updated successfully")
        self.settings_window.close()
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
            weather = get_weather(city)
            if weather and all(weather.values()):
                icon = icons.get(weather['icon'], '❓') # ля какая иконка 
                self.weather_label.setText(f"{icon}  {weather['temperature']}°C")
                self.weather_desc.setText(f"Погода: {weather['description']}")
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


if __name__ == "__main__":
    if not load_config():
        create_config()
    app = QApplication(sys.argv)
    window = SettingsWindow()
    window.start_telegram_bot()
    window.show()
    sys.exit(app.exec())


