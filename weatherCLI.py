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

headers = {  # nominatim f. nominatim
    'User-Agent':'WeatherCLI (duelger.cem@gmail.com)'
        }

def weatherCode(current_weather_code):
    print("test def")
    print(current_weather_code)

# definier optionen
parser = argparse.ArgumentParser(prog='weatherCLI', description='Weather  Client for ZIP Code or GPS ')
parser.add_argument('-v', '--version', action='store_true', help='shows program Version')
parser.add_argument('-z', '--ZIP_Code', type=str, help='Works only with German Postleitzahl')

opt = parser.parse_args()
print()
print()
print(ascii_banner)
print()

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

                print(f"Your Location: {pos_name}\n")
                print(f"Current Temp: {round(current_temperature_2m,2)}")
                print(f"Feels Like: {round(current_apparent_temperature,2)}")
                print(f"bei tag ausgabe 1.0 bein nacht:{current_is_day}") # noch zu verändern
                print(f"Precipitation: {current_precipitation} mm")
                print(f"Wind: {round(current_wind_speed_10m,2)} km/h")
                print(f"Humidity: {current_relative_humidity_2m} %")
                print(f"{current_weather_code}")
                weatherCode(current_weather_code)
                



                




            
            except requests.exceptions.RequestException as e:
                print(f"meteo api error : {e}")  

        else: print("error occurred, PLZ not found")


    except requests.exceptions.RequestException as e:
        print(f"error occurred: {e}")
    
    

