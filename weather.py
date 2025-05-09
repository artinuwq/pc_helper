from config import AK_weather, city
import requests
url = 'https://api.openweathermap.org/data/2.5/weather?q='+city+'&units=metric&lang=ru&appid='+AK_weather

icon = {
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




def get_weather():
    weather_data = requests.get(url).json()


    temperature = round(weather_data['main']['temp'])
    temperature_feels = round(weather_data['main']['feels_like'])
    humidity = round(weather_data['main']['humidity'])
    wind_speed = round(weather_data['wind']['speed'])
    weather_description = weather_data['weather'][0]['description']
    icon = weather_data['weather'][0]['icon']

    return {"temperature":temperature, 
            'temperature_feels':temperature_feels, 
            'humidity':humidity, 
            'wind_speed':wind_speed, 
            'weather_data':weather_data, 
            'weather_description':weather_description, 
            'icon':icon
            }

if __name__ == '__main__':
    data = get_weather()
    #print(data['weather_data'], '\n')
    print('Погода в городе', city, '🏙️')
    print('    ' + data['weather_description'].capitalize() + ' ' + icon[data['icon']])
    print('    Температура:', data['temperature'], '°C')
    print('    Ощущается как:', data['temperature_feels'], '°C')
