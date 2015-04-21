#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Kyle Fitzsimmons, 2015
import serial
import time
import threading

data = {}

def update_watcher():
    global data
    address = '/dev/ttyACM0'
    try:
        ser = serial.Serial(address, 9600)
    except OSError:
        data['error'] = 'No arduino found on: {}'.format(address)
        return
    seen_hello_msg = False
    while True:
        msg = ser.readline().rstrip()
        line = msg.split('--')
        if seen_hello_msg is False and 'Connection established' in line:
            seen_hello_msg = True
        elif seen_hello_msg:
            sensor, reading = line
            data[sensor] = reading
        time.sleep(1)

def run():
    updates = threading.Thread(target=update_watcher)
    updates.daemon = True
    updates.start()

def last_reading(db, now):
    global data
    if 'error' in data:
        log_msg = ('{now}: No gardenbot data available'.format(now=now))
    elif data:
        temp_c = data['tempC']
        temp_f = '{:.2f}'.format(float(temp_c) * 1.8 + 32)
        photo_level = data['photolvl']
        log_msg = '{now}: {celsius}°C/{fahrenheit}°F | Light level: {light}'.format(
            now=now, 
            celsius=temp_c, 
            fahrenheit=temp_f, 
            light=photo_level
            )
        db['gardenbot'].insert({'timestamp': now, 'tempC': temp_c, 'photoLvl': photo_level})
    else:
        log_msg = '{now}: Arduino module failed'
    irc_msg = log_msg
    return log_msg, irc_msg

