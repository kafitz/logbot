#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Kyle Fitzsimmons, 2015
import csv
from datetime import datetime
import requests
import lxml.html

csvdir = './modules/waterlevels'

def write_csv(output_data):
    csv_filename = '{dir}/{date}.csv'.format(dir=csvdir, date=datetime.now().strftime('%Y%m%d'))
    with open(csv_filename, 'wb') as csv_out:
        writer = csv.writer(csv_out)
        writer.writerows(output_data)

def update(db, now):
    url = 'http://www.tides.gc.ca/eng/station?type=1&sid=15540&tz=EDT&pres=2'
    r = requests.get(url)

    output_data = []
    if r.status_code is 200:
        tree = lxml.html.fromstring(r.text)

        header_content = tree.xpath('//div[@class="stationTextHeader"]')
        if header_content:
            div = header_content[0]
            for child in div.getchildren():
                output_data.append(child.text.replace('#', '').strip().encode('utf-8').split(';'))

        data_content = tree.xpath('//div[@class="stationTextData"]')
        if data_content:
            div = data_content[0]
            for child in div.getchildren():
                output_data.append(child.text.strip().encode('utf-8').split(';'))

        write_csv(output_data)

        # consume first 3 rows (junk)
        output_data = output_data[3:]
        headers = [h.lower() for h in output_data.pop(0)]
        db_data = [dict(zip(headers, row)) for row in output_data]

        for row in db_data:
            db.upsert('tides', row, ['date', 'time'])

        log_msg = '{now}--Updated water levels data from {url}'.format(
            now=now,
            url=url)
    else:
        log_msg = '{now}--Unable to fetch water levels from {url}'.format(
            now=now,
            url=url
            )
    irc_msg = log_msg
    return log_msg, irc_msg

if __name__ == '__main__':
    from databaser import Database
    from datetime import datetime
    db = Database('./test.sqlite')
    now = datetime.now().replace(microsecond=0)
    update(db, now)



