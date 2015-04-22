#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Kyle Fitzsimmons, 2015
import config
from databaser import Database
from datetime import datetime
import mailer
from redis_pub import RedisMessage
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

dbfile = './records.sqlite'
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
    db = Database(dbfile)

    log_msgs.append('')
    log_file(log_msgs)
    db.close()

def fifteenminute_updates():
    log_msgs = []    
    now = datetime.now().replace(microsecond=0)
    db = Database(dbfile)

    # arduino
    arduino_log, arduino_irc = arduino.last_reading(db, now)
    log_msgs.append(arduino_log)
    log_irc(arduino_irc)

    # craigslist
    craigslist_log, craigslist_irc = craigslist.search(db, now)
    log_msgs.append(craigslist_log)
    log_irc(craigslist_irc)

    # weather
    weather_log, weather_irc = weather.current(db)
    log_msgs.append(weather_log)
    log_irc(weather_irc)

    log_msgs.append('')
    log_file(log_msgs)
    db.close()

def halfday_updates():
    log_msgs = []
    now = datetime.now().replace(microsecond=0)
    db = Database(dbfile)

    log_irc('{now}--Checking for new GTFS files'.format(now=now))
    gtfs_log, gtfs_email = transitfeeds.check_for_gtfs(db, cfg)
    log_msgs.extend(gtfs_log)
    if gtfs_email:
        log_irc('{now}--Emailing about GTFS update'.format(now=now))
        mailer.send(cfg, gtfs_email)

    log_msgs.append('')
    log_file(log_msgs)
    db.close()

#### specially scheduled tasks
def waterlevel_update():
    log_msgs = []
    db = Database(dbfile)
    now = datetime.now().replace(microsecond=0)
    tides_log, tides_irc = waterlevels.update(db, now)
    log_msgs.append(tides_log)
    log_irc(tides_irc)

    log_msgs.append('')
    log_file(log_msgs)
    db.close()


def run_threaded(job):
    t = threading.Thread(target=job)
    t.start()

def main():
    # initialize garduino watcher
    arduino.run()

    ## schedule waits so do first run immediately
    # schedule.every(15).seconds.do(run_threaded, test_updates) # debugger
    # schedule.every(5).minutes.do(run_threaded, fiveminute_updates)
    schedule.every(15).minutes.do(run_threaded, fifteenminute_updates)
    schedule.every(12).hours.do(run_threaded, halfday_updates)
    schedule.run_all()    
    schedule.every().day.at('6:05').do(run_threaded, waterlevel_update)
    while True:
        schedule.run_pending()
        time.sleep(5)

if __name__ == '__main__':
    main()
