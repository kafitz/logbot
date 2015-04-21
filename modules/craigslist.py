#!/usr/bin/env python
# Kyle Fitzsimmons, 2015
from datetime import datetime
import dataset
import requests
from lxml import html

db = dataset.connect('sqlite:///../records.sqlite')
if not 'craigslist' in db.tables:
    db.create_table('craigslist', primary_id='id')

def xpath_findone(tree, query):
    '''A get function to return either the first result
        or None if the xpath query fails to find an element'''
    try:
        (element,) = tree.xpath(query)
    except ValueError:
        return None
    return element

def posts(parameters):
    scrape_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    base_url, search_url = parameters['base_url'], parameters['search_url']
    del parameters['base_url']
    del parameters['search_url']
    response = requests.get(base_url + search_url, params=parameters)
    tree = html.fromstring(response.text)
    rows = tree.xpath('//p[@class="row"]')
    posts = []
    for row in rows:
        post = {'scrape_time': scrape_time}
        url = xpath_findone(row, 'a/@href')
        post['url'] = base_url + url
        subrow = xpath_findone(row, './/span[@class="pl"]')
        post['id'] = xpath_findone(subrow, 'a/@data-id')
        post['timestamp'] = xpath_findone(subrow, 'time/@datetime')
        post['text'] = xpath_findone(subrow, 'a/text()')
        post['repost_id'] = xpath_findone(subrow, 'a/@data-repost-of') # check for a repost id
        posts.append(post)
    return posts

def search(db, now):
    parameters = {
        'base_url': 'http://montreal.en.craigslist.ca',
        'search_url': '/search/bia',
        'query' : None,
        'minAsk': None,
        'maxAsk': 600,
        'sort': 'rel'
    }
    results = posts(parameters.copy())

    # update database and determine which posts are new to report
    new_results = []
    for post in results:
        if not db['craigslist'].find_one(id=post['id']):
            new_results.append(post)
            db['craigslist'].insert(post)
        else:
            db['craigslist'].upsert(post, ['id'])

    # file output log message
    min_ask = parameters['minAsk'] or 0
    max_ask = parameters['maxAsk'] or 'inf'
    log_msg = '{now}--Craigslist | {url} | ${min}-{max}'.format(
        now=now,
        url=parameters['search_url'], 
        min=min_ask,
        max=max_ask
        )
    if parameters['query']:
        log_msg += ' | {}: '
    else:
        log_msg += ': '
    log_msg += '{{num} new results'.format(num=len(new_results))

    irc_msgs = []
    for post in new_results:
        print(post)
        msg = '{now}--Craigslist: {text} ({time}) - {url}'.format(
            now=now,
            text=post['text'].encode('utf-8'),
            time=post['timestamp'],
            url=post['url']
        )
        irc_msgs.append(msg)
    if not irc_msgs:
        irc_msgs = log_msg

    return log_msg, irc_msgs


