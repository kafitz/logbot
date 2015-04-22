#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
    # try:
    response = requests.get(url, params=parameters)
    data = response.json()
    pprint(data)
    celsius = data['main']['temp'] - 273.15
    fahrenheit = (celsius * 1.8) + 32
    weather_entry = {
        'time': now,
        'temperature_c': celsius,
        'temperature_f': fahrenheit,
        'humidity': data['main']['humidity'],
        'sunrise': data['sys']['sunrise'],
        'sunset': data['sys']['sunset'],
        'cloud_cover': data['clouds']['all'],
    } 
    
    db.insert('weather', weather_entry)
    log_msg = '{now}--Weather: {c:.1f}°C/{f:.1f}°F, RH: {rh}, Cloud cover: {cc}%'.format(
        now=now,
        c=celsius,
        f=fahrenheit,
        rh=data['main']['humidity'],
        cc=data['clouds']['all']
        )
    # except Exception, e:
    #     log_msg = '{}--weather update failed: {}'.format(now, e)
    irc_msg = log_msg
    return log_msg, irc_msg

if __name__ == '__main__':
    from databaser import Database
    db = Database('./test.sqlite')
    log_msg, irc_msg = current(db)
    print(log_msg)

