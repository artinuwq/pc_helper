import sys
from weather import get_weather, icons  # Импортируем функцию получения погоды
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QCheckBox
from PyQt6.QtGui import QFont
from PyQt6.QtCore import QTimer, Qt

import psutil
import GPUtil

class SettingsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Настройки")
        self.setGeometry(100, 100, 100, 200)

        self.initUI()
        self.update_weather()
        self.update_stats()

        # Таймеры для обновления данных
        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self.update_stats)
        self.stats_timer.start(1000)  

        self.weather_timer = QTimer()
        self.weather_timer.timeout.connect(self.update_weather)
        self.weather_timer.start(600000)  

    def initUI(self):
        main_layout = QHBoxLayout()

        # Левая часть (бот и погода)
        left_layout = QVBoxLayout()
        bot_status = QLabel("Бот выключен")  # Changed checkbox to label
        bot_status.setFont(QFont("Arial", 16))
        left_layout.addWidget(bot_status)

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

        main_layout.addLayout(left_layout)

        #системные ресурсы
        right_layout = QVBoxLayout()
        self.cpu_label = QLabel("CPU: ...%")
        self.gpu_label = QLabel("GPU: ...%")
        self.ram_label = QLabel("RAM: ...%")

        for lbl in [self.cpu_label, self.gpu_label, self.ram_label]:
            lbl.setFont(QFont("Arial", 16))
            right_layout.addWidget(lbl)

        main_layout.addLayout(right_layout)
        self.setLayout(main_layout)



    def update_weather(self):
        weather = get_weather()
        icon = icons[weather['icon']]
        self.weather_label.setText(f"{icon}  {weather['temperature']}°C")
        self.weather_desc.setText(f"Погода: {weather['description']}")
        self.feels_like_label.setText(f"Ощущается как: {weather['temperature_feels']}°C")



    def update_stats(self):
        # CPU and RAM stats
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        gpus = GPUtil.getGPUs() # Get GPU stats
        gpu = gpus[0].load * 100  # Convert to percentage
        self.gpu_label.setText(f"GPU: {gpu:.1f}%")

        # Update labels
        self.cpu_label.setText(f"CPU: {cpu}%")
        self.ram_label.setText(f"RAM: {ram}%")
