#!/usr/bin/env python
# Kyle Fitzsimmons, 2015
from datetime import datetime
import requests

def current(db):
    location = 'Montreal,QC'
    parameters = {
        'q': location
    }
    url = 'http://api.openweathermap.org/data/2.5/weather'
    now = datetime.now().replace(microsecond=0)
    try:
        response = requests.get(url, params=parameters)
        data = response.json()
        celsius = data['main']['temp'] - 273.15
        fahrenheit = (celsius * 1.8) + 32
        weather_entry = {
            'time': now,
            'temperature_c': celsius,
            'temperature_f': fahrenheit,
            'humidity' : data['main']['humidity'],
            'sunrise': data['sys']['sunrise'],
            'sunset': data['sys']['sunset'],
            'cloud_cover': data['clouds']['all'],
        } 
        
        db['weather'].insert(weather_entry)
        log_msg = '{} -- weather update successful'.format(now)
    except Exception, e:
        log_msg = '{} -- weather update failed: {}'.format(now, e)
    return [log_msg]
