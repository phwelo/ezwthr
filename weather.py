#!/usr/bin/python3

import requests
import socket
import os.path
import configparser
import json
import sys
from pathlib import Path
# Check for config file and values, give appropriate errors
def check_home_config(conf):
  return os.path.isfile(conf)

# Bring in the config and format better than configparser does
def config_handler(conf_path):
  config = configparser.ConfigParser()
  config.read(conf_path)
  result = {
    'geo_api': config.get('ezwthr', 'geo_api'),
    'weather_api': config.get('ezwthr', 'weather_api'),
    'temp_toggle': config.getboolean('ezwthr', 'show_temperature'),
    'icons': {
      1: config.get('icons', 'sunny'),
      2: config.get('icons', 'mostly_sunny'),
      3: config.get('icons', 'cloudy'),
      4: config.get('icons', 'more_cloudy'),
      9: config.get('icons', 'light_rain'),
      10: config.get('icons', 'rainy'),
      11: config.get('icons', 'thunderstorm'),
      13: config.get('icons', 'snow'),
      50: config.get('icons', 'fog')
    }
  }
  return result

# Grab the public IP address so that we can geolocate it
def public_ip():
  return requests.get('https://api.ipify.org?format=json').json()['ip']

# Grab geolocation info so that we can get the weather for it
def get_geo_data(public_ip, api_key):
  geodata = requests.get('https://api.ipgeolocation.io/ipgeo?apiKey={0}&ip={1}'.format(api_key, public_ip))
  if geodata.status_code == 401:
    raise ValueError('That API key is no good.  Go to https://ipgeolocation.io/signup and get a key.')
    sys.exit(1)
  return (geodata.json()['latitude'],geodata.json()['longitude'])

def get_weather_info(geo_coords, api_key):
  current = requests.get('http://api.openweathermap.org/data/2.5/weather?lat={0}&lon={1}&appid={2}'.format(geo_coords[0], geo_coords[1], api_key))
  if current.status_code == 401:
    raise ValueError('That API key is no good. Go to https://home.openweathermap.org/ to get a key')
    sys.exit(1)
  return current

# Get the weather for current location and return the proprietary icon index for it
def get_weather_icon_index(weather_info): 
  return weather_info.json()['weather'][0]['icon'][:-1]

def get_temperature(weather_info):
  kelvin = weather_info.json()['main']['temp']
  # Conversion of kelvin to farenheit
  return int(1.8 * (kelvin - 273) + 32)

# Cross reference our list with the current conditions, return an icon
def retrieve_weather_icon(index, icon_dict):
  return icon_dict[int(index)]

def create_config(conf_file):
  default_config = """
  [ezwthr]
  # API key for https://app.ipgeolocation.io/
  geo_api: place_the_api_key_here
  # API key for https://openweathermap.org/
  weather_api: place_the_api_key_here
  show_temperature: True
  [icons]
  sunny: 🌣
  mostly_sunny: 🌤
  cloudy: 🌥
  more_cloudy: 🌥
  light_rain: 🌦
  rainy: 🌧
  thunderstorm: 🌩
  snow: 🌨
  fog: 🌫
  """
  conf_file = open(conf_file, 'w')
  conf_file.write(default_config)
  conf_file.close()
  return

CONF_LOCATION = str(Path.home()) + '/.config/ezwthr.conf'
True if check_home_config(CONF_LOCATION) else create_config(CONF_LOCATION)

settings = config_handler(CONF_LOCATION)
public_ip_address = public_ip()
coords = get_geo_data(public_ip_address, settings['geo_api'])
weather = get_weather_info(coords, settings['weather_api'])
icon_index = get_weather_icon_index(weather)
temp = get_temperature(weather)
# Output the icon to stdout
print(retrieve_weather_icon(icon_index, settings['icons']), end="")
print(str(temp) + '°F') if settings['temp_toggle'] else None