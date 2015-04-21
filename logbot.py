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
from modules import craigslist
from modules import transitfeeds
from modules import waterlevels
from modules import weather

cfg = config.load()
if not cfg:
    print('No previous settings.yaml found, first edit the default in logbot folder.')
    sys.exit()

R = RedisMessage()

def log_file(messages):
    with open('status.txt', 'a') as log_f:
        for log_msg in messages:
            log_f.write(log_msg + '\n')

def log_irc(messages):
    if isinstance(messages, list):
        for msg in messages:
            R.send(msg)
    elif isinstance(messages, basestring):
        R.send(messages)

### recurring interval tasks
def test_updates():
    '''DEBUGGER'''
    db = dataset.connect('sqlite:///records.sqlite')

def fiveminute_updates():
    log_msgs = []
    now = datetime.now().replace(microsecond=0)
    db = dataset.connect('sqlite:///records.sqlite')

    # arduino
    arduino_log, arduino_irc = arduino.last_reading(db, now)
    log_msgs.append(arduino_log)
    log_irc(arduino_irc)

    log_msgs.append('')
    log_file(log_msgs)

def fifteenminute_updates():
    log_msgs = []    
    now = datetime.now().replace(microsecond=0)
    db = dataset.connect('sqlite:///records.sqlite')

    # craigslist
    craigslist_log, craigslist_irc = craigslist.search(db)
    log_msgs.append(craigslist_log)
    log_irc(craigslist_irc)

    # weather
    log_irc('{now}: Checking weather...'.format(now=now))
    weather_log = weather.current(db)
    log_msgs.extend(weather_log)

    log_msgs.append('')
    log_file(log_msgs)    

def halfday_updates():
    log_msgs = []
    now = datetime.now().replace(microsecond=0)
    db = dataset.connect('sqlite:///records.sqlite')
    status_prefix = '{} - 1-day update'.format(now)

    log_irc('{}: Checking for new GTFS files...'.format(status_prefix))
    gtfs_log, gtfs_email = transitfeeds.check_for_gtfs(cfg, db)
    log_msgs.extend(gtfs_log)
    if gtfs_email:
        log_irc('{}: Emailing about GTFS update...'.format(now))
        mailer.send(cfg, gtfs_email)

    log_msgs.append('')
    log_file(log_msgs)

#### specially scheduled tasks
def waterlevel_update():
    db = dataset.connect('sqlite:///records.sqlite')
    now = datetime.now().replace(microsecond=0)
    status = '{} - Scheduled water levels update'.format(now)
    log_irc(status)
    tides = waterlevels.update()
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
    # schedule.every(15).seconds.do(run_threaded, test_updates) # debugger
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
