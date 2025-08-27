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

version = '0.1 beta'
land = 'Germany'
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
parser.add_argument('-v', '--version', action='store_true', help='shows program Version')
parser.add_argument('-z', '--ZIP_Code', type=str, help='Works only with German Postleitzahl')

opt = parser.parse_args()
print()
print()
print(ascii_banner)
#print("-z [German Zip Code] / -h for help\n\n")

if opt.version:
    print(version)
if opt.ZIP_Code:
    plz = opt.ZIP_Code
    uri_pos = f"https://nominatim.openstreetmap.org/search?format=json&postalcode={plz}&country={land}"

    try: # 
        pos_data_raw = requests.get(uri_pos, headers=headers)
        pos_data = pos_data_raw.json()
        lat = pos_data[0].get('lat')
        lon = pos_data[0].get('lon')
        pos_name = pos_data[0].get('display_name')
        rank = pos_data[0].get('place_rank')

        if rank == 21:
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
                print(f"Precipitation: {current_precipitation} mm")
                print(f"Condition: {day}, {weather_txt}")
                
                if current_showers > 0.0:
                    print(f"Current shower: \033[31m{current_showers}\033[0m")
                if current_rain > 0.0:
                    print(f"current Rain: \033[31m{current_rain}\033[0m")
                if current_snowfall > 0.0:
                    print(f"Current Snowfall: \033[31m{current_snowfall}\033[0m")

                #print(current_wind_direction_10m)
                
            except requests.exceptions.RequestException as e:
                print(f"meteo api error : {e}")  

        else: print("error occurred, PLZ not found")


    except requests.exceptions.RequestException as e:
        print(f"error occurred: {e}")
    
