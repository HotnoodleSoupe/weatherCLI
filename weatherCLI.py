#!/home/cem/py/weatherCLI/.venv/bin/python
import argparse
import requests
import openmeteo_requests
import requests_cache
from retry_requests import retry

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

select_counter = 0
#land = 'Germany'
ascii_banner = """
       .--.
    _.-(    ).--.
  .'(   _ `).   _ )
 (  `.' WeatherCLI _.'  `
  `.'`' '`'.'`
     """

wmo_codes = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast", 45: "Fog", 48: "Depositing rime fog", 51: "Light Drizzle", 53: "Moderate Drizzle", 55: "Dense Drizzle", 56: "Light Freezing Drizzle", 57: "Dense Freezing Drizzle",
    61: "Slight Rain", 63: "Moderate Rain", 65: "Heavy Rain", 66: "Light Freezing Rain", 67: "Heavy Freezing Rain", 71: "Slight Snow fall", 73: "Moderate Snow fall", 75: "Heavy Snow fall", 77: "Snow grains", 80: "Slight Rain showers", 81: "Moderate Rain showers",
    82: "Violent Rain showers", 85: "Slight Snow showers", 86: "Heavy Snow showers", 95: "Slight or moderate Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail"
}

headers = {  
    'User-Agent':'WeatherCLI (duelger.cem@gmail.com)'
        }

# definier optionen
parser = argparse.ArgumentParser(prog='weatherCLI', description='Weather  Client for ZIP Code or GPS ')
parser.add_argument('-a', '--about', action='store_true', help='about')
parser.add_argument('-l', '--location', type=str, help='Works only with German Postleitzahl')

opt = parser.parse_args()
print()
print()
print(ascii_banner)

if opt.about:
    print("""
    About WeatherCLI
    WeatherCLI is a lightweight, command-line weather tool that provides real-time weather data 
    and forecasts directly in your terminal. It's built for developers and anyone who wants quick, 
    no-frills access to essential weather information without leaving their command line.

    The application leverages the power of the Open-Meteo API to retrieve highly accurate, 
    model-based weather data. It is developed using Python, which handles all API requests, 
    data parsing, and output formatting.

    Version: 0.2 beta
    Copyright (c) 2025 Cem Dülger
    Contact: SynapticTwin@0xl4b.dev

    Key Features:

    Real-Time Data: Get current temperature, wind speed, and precipitation.

    Location-Based: Simply enter a postal code to receive weather data for your specific location.

    Minimalist Design: A clean and efficient command-line interface.

    WeatherCLI is an open-source project and is licensed under the MIT License. Contributions are welcome!
    """)
if opt.location:

    loc = opt.location
    uri_pos = f"https://nominatim.openstreetmap.org/search?format=json&q={loc}"
    
    try: 

        pos_data_raw = requests.get(uri_pos, headers=headers)
        loc_data = pos_data_raw.json()
        
        for location in loc_data: # lauft durch jedes element in der liste und weist ihm die variable location für weiter opertionen (if) bis alle ellemente abgearbeitet sind
            pos_name = location.get('display_name')
            select_counter = select_counter + 1 
            
            print(f"<< {select_counter} >> - {pos_name}")
            print()

        user_select_raw = int(input("Select your loacation: "))
        print()
        user_select = user_select_raw - 1

        lat = loc_data[user_select].get('lat')
        lon = loc_data[user_select].get('lon')
            
        url_meteo = "https://api.open-meteo.com/v1/forecast"
        params = {
            f"latitude": {lat},
            f"longitude": {lon},
            "current": ["temperature_2m", "relative_humidity_2m", "apparent_temperature", "is_day", "precipitation", "rain", "showers", "snowfall", "weather_code", "cloud_cover", "wind_speed_10m", "wind_direction_10m"],
            }

        try:
            response_meteo = openmeteo.weather_api(url_meteo,params=params)
            meteo_data = response_meteo[0]

            current = meteo_data.Current()
            current_temperature_2m = current.Variables(0).Value()
            current_relative_humidity_2m = current.Variables(1).Value()
            current_apparent_temperature = current.Variables(2).Value()
            current_is_day = current.Variables(3).Value()
            current_precipitation = current.Variables(4).Value()
            current_rain = current.Variables(5).Value()
            current_showers = current.Variables(6).Value()
            current_snowfall = current.Variables(7).Value()
            current_weather_code = current.Variables(8).Value()
            current_cloud_cover = current.Variables(9).Value() # wird vermutlich nicht genutzt
            current_wind_speed_10m = current.Variables(10).Value()
            current_wind_direction_10m = current.Variables(11).Value() # wird vermutlich nicht genutzt
            weather_txt = wmo_codes.get(current_weather_code)
            if current_is_day == 1:
                day = "Day"
            else: day = "Night"
                    
            print(f"Location: {pos_name}\n")
            print(f"Current Temp: {round(current_temperature_2m,2)}°C / Feels Like: {round(current_apparent_temperature,2)}°C")
            print(f"Humidity: {current_relative_humidity_2m} %")
            print(f"Wind: {round(current_wind_speed_10m,2)} km/h")
            print(f"Precipitation: {round(current_precipitation,2)} mm")
            print(f"Condition: {day}, {weather_txt}")
                    
            if current_showers > 0.0:
                print(f"Current shower: \033[31m{round(current_showers,2)} mm\033[0m")
            if current_rain > 0.0:
                print(f"current Rain: \033[31m{round(current_rain,2)} mm\033[0m")
            if current_snowfall > 0.0:
                print(f"Current Snowfall: \033[31m{round(current_snowfall,2)} mm\033[0m")
            
        except requests.exceptions.RequestException as e:
            print(f"meteo api error : {e}")  

        


    except requests.exceptions.RequestException as e:
        print(f"error occurred: {e}")
    