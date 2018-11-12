#!/usr/bin/python3

import requests
import socket
import settings

# Grab the public IP address so that we can geolocate it
def public_ip():
  return requests.get('https://api.ipify.org?format=json').json()['ip']

# Grab geolocation info so that we can get the weather for it
def get_geo_data(public_ip, api_key):
  geodata = requests.get('https://api.ipgeolocation.io/ipgeo?apiKey={0}&ip={1}'.format(api_key, public_ip))
  return (geodata.json()['latitude'],geodata.json()['longitude'])

# Get the weather for current location and return the proprietary icon index for it
def get_weather_icon_index(geo_coords, api_key):
  current = requests.get('http://api.openweathermap.org/data/2.5/weather?lat={0}&lon={1}&appid={2}'.format(geo_coords[0], geo_coords[1], api_key))
  return current.json()['weather'][0]['icon'][:-1]

# Cross reference our list with the current conditions, return an icon
def retrieve_weather_icon(index, icon_dict):
  return icon_dict[int(index)]

public_ip_address = public_ip()
coords = get_geo_data(public_ip_address, settings.GEO_API_KEY)
icon_index = (get_weather_icon_index(coords, settings.OPEN_WEATHER_MAP_API_KEY))
# Output the icon to stdout
print(retrieve_weather_icon(icon_index, settings.WEATHER_ICONS), end="")
