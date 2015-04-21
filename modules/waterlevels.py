import csv
from datetime import datetime
import requests
import lxml.html

csvdir = './modules/waterlevels'
url =    'http://www.tides.gc.ca/eng/station?type=1&sid=15540&tz=EDT&pres=2'

def write_csv(output_data):
    csv_filename = '{dir}/{date}.csv'.format(dir=csvdir, date=datetime.now().strftime('%Y%m%d'))
    with open(csv_filename, 'wb') as csv_out:
        writer = csv.writer(csv_out)
        writer.writerows(output_data)

def update():
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
    return db_data
