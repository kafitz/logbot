#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Kyle Fitzsimmons, 2015
import config
import dataset
from datetime import datetime
import mailer
from redis_pub import RedisMessage
import requests
import schedule
import sys
import time
import threading
# modules
from modules import arduino
from modules import transitfeeds
from modules import waterlevels
from modules import weather

cfg = config.load()
if not cfg:
    print('No previous settings.yaml found, first edit the default in logbot folder.')
    sys.exit()

R = RedisMessage()

def log_results(messages):
    with open('status.txt', 'a') as log_f:
        for log_msg in messages:
            log_f.write(log_msg + '\n') 

### recurring interval tasks
def fiveminute_updates():
    log_msgs = []
    now = datetime.now().replace(microsecond=0)
    db = dataset.connect('sqlite:///records.sqlite')
    status_prefix = '{} - 5-minute update'.format(now)

    log_msgs.append('')
    log_results(log_msgs)

def fifteenminute_updates():
    log_msgs = []    
    now = datetime.now().replace(microsecond=0)
    db = dataset.connect('sqlite:///records.sqlite')
    status_prefix = '{} - 15-minute update'.format(now)

    gardenbot_info = arduino.last_reading()
    if gardenbot_info:
        temp_c = gardenbot_info['tempC']
        temp_f = '{:.2f}'.format(float(temp_c) * 1.8 + 32)
        photo_level = gardenbot_info['photolvl']
        R.send('{prefix}: {celsius}°C/{fahrenheit}°F | Light level: {light}'.format(
            prefix=status_prefix, 
            celsius=temp_c, 
            fahrenheit=temp_f, 
            light=photo_level)
        )

        db['gardenbot'].insert({'timestamp': now, 'tempC': temp_c, 'photoLvl': photo_level})
    else:
        R.send('{prefix}: No gardenbot data available'.format(prefix=status_prefix))

    R.send('{prefix}: Checking weather...'.format(prefix=status_prefix))
    weather_msg = weather.current(db)
    log_msgs.extend(weather_msg)

    log_msgs.append('')
    log_results(log_msgs)    

def halfday_updates():
    log_msgs = []
    now = datetime.now().replace(microsecond=0)
    db = dataset.connect('sqlite:///records.sqlite')
    status_prefix = '{} - 1-day update'.format(now)

    R.send('{}: Checking for new GTFS files...'.format(status_prefix))
    gtfs_msgs, email_msg = transitfeeds.check_for_gtfs(cfg, db)
    log_msgs.extend(gtfs_msgs)
    if email_msg:
        R.send('{}: Emailing about GTFS update...'.format(now))
        mailer.send(cfg, email_msg)

    log_msgs.append('')
    log_results(log_msgs)

#### specially scheduled tasks
def waterlevel_update():
    db = dataset.connect('sqlite:///records.sqlite')
    now = datetime.now().replace(microsecond=0)
    status = '{} - Scheduled water levels update'.format(now)
    R.send(status)
    tides = waterlevels.update()
    # first run
    if not 'tides' in db:
        db['tides'].insert_many(tides)
    else:
        for row in tides:
            db['tides'].upsert(row, ['date'])


def run_threaded(job):
    t = threading.Thread(target=job)
    t.start()


def main():
    # initialize garduino watcher
    arduino.run()

    ## schedule waits so do first run immediately
    schedule.every(5).minutes.do(run_threaded, fiveminute_updates)
    schedule.every(15).minutes.do(run_threaded, fifteenminute_updates)
    schedule.every(12).hours.do(run_threaded, halfday_updates)
    schedule.run_all()    
    schedule.every().day.at('6:05').do(run_threaded, waterlevel_update)
    while True:
        schedule.run_pending()
        time.sleep(5)

if __name__ == '__main__':
    main()
