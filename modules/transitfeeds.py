#!/usr/bin/env python
# Kyle Fitzsimmons, 2015
from datetime import datetime
import requests

def check_for_gtfs(config, db):
    log_msgs = []
    agencies = {
        'stm': 'societe-de-transport-de-montreal/39',
        'mbta': 'mbta/64'
    }
    url = 'http://api.transitfeeds.com/v1/getFeedVersions'

    now = datetime.now().replace(microsecond=0)
    send_email = False
    msg = 'New GTFS updates found on {}\n\n'.format(now)
    for shorthand, feed in agencies.items():
        parameters = {
            'key': config.modules.transitfeeds_api,
            'feed': feed
        }

        try:
            response = requests.get(url, params=parameters)
            results = response.json().get('results')
            if results:
                latest = results['versions'][0]
                latest_dt = datetime.fromtimestamp(latest['ts'])
                latest_release = {
                    'agency': shorthand,
                    'date': latest_dt
                }

                last_known_gtfs = db['gtfs'].find_one(agency=shorthand)
                if latest_release > last_known_gtfs:
                    send_email = True

                msg += '{}: {}\n'.format(shorthand, latest_release > last_known_gtfs)
                db['gtfs'].upsert(latest_release, ['agency'])
                log_msgs.append('{} -- {} gtfs check successful'.format(now, shorthand))
            else:
                log_msgs.append('{} -- {} gtfs check: no results found'.format(now, shorthand))
        except Exception, e:
            log_msgs.append('{} -- gtfs check failed: {}'.format(now, e))

    email_msg = None
    if send_email:
        email_msg = {
            'subject': 'raspi -- GTFS updates found',
            'body': msg
        }
    return log_msgs, email_msg
