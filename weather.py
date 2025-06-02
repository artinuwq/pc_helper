#from config import AK_weather, city
import requests
import json


icons = {
    '01d': '☀️',  # Clear sky sun
    '01n': '🌙',  # Clear sky moon
    '02d': '🌤️',  # Few clouds sun
    '02n': '🌥️',  # Few clouds moon
    '03d': '☁️', '03n': '☁️',  # Scattered clouds
    '04d': '☁️', '04n': '☁️',  # Broken clouds
    '09d': '🌧️', '09n': '🌧️',  # Shower rain
    '10d': '🌦️',  # Rain sun
    '10n': '🌧️',  # Rain moon
    '11d': '⛈️',  # Thunderstorm
    '11n': '⛈️',  # Thunderstorm
    '13d': '❄️',  '13n': '❄️',  # Snow
    '50d': '🌫️',  # Mist
    }

def get_weather(city, AK_weather):
    url = 'https://api.openweathermap.org/data/2.5/weather?q='+city+'&units=metric&lang=ru&appid='+AK_weather
    weather_data = requests.get(url).json()
    temperature = round(weather_data['main']['temp'])
    temperature_feels = round(weather_data['main']['feels_like'])
    humidity = round(weather_data['main']['humidity'])
    wind_speed = round(weather_data['wind']['speed'])
    description = weather_data['weather'][0]['description']
    icon = weather_data['weather'][0]['icon']

    return {"temperature":temperature, 
            'temperature_feels':temperature_feels, 
            'humidity':humidity, 
            'wind_speed':wind_speed, 
 #           'weather_data':weather_data, 
            'description':description, 
            'icon':icon
            }

if __name__ == '__main__':
        # Читаем конфиг
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    city = config.get('city', 'Москва')
    api_key = config.get('AK_weather', '')

    data = get_weather(city, api_key)
    print('Погода в городе', city, '🏙️')
    print('    ' + data['description'].capitalize() + ' ' + data['icon'])
    print('    Температура:', data['temperature'], '°C')
    print('    Ощущается как:', data['temperature_feels'], '°C')
