import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QCheckBox
from PyQt6.QtGui import QFont
from PyQt6.QtCore import QTimer, Qt

from weather import get_weather, icons  # Импортируем функцию получения погоды
from interface import SettingsWindow  # Импортируем класс окна настроек



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SettingsWindow()
    window.show()
    sys.exit(app.exec())



'''
Контроль работы тг бота 
вывод погоды и нагрузки на пк 
Все это из интерфейса

'''