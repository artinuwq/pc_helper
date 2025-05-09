from config import AK_weather, city
import requests
url = 'https://api.openweathermap.org/data/2.5/weather?q='+city+'&units=metric&lang=ru&appid='+AK_weather


weather_data = requests.get(url).json()


temperature = round(weather_data['main']['temp'])
temperature_feels = round(weather_data['main']['feels_like'])
humidity = round(weather_data['main']['humidity'])
wind_speed = round(weather_data['wind']['speed'])

if __name__ == '__main__':
    print(weather_data, '\n')
    print('Сейчас в городе', city, str(temperature), '°C')
    print('Ощущается как', str(temperature_feels), '°C')
    print('Скорость ветра', str(wind_speed), '°C')
    print('Влажность', str(humidity), '%') 
