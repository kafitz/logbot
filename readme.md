### Logbot
Logbot is a simple logging framework designed to be modular for recording sensors,
scraping the internet, and running tasks. Logbot is written to be simple first and
catered to run on a Raspberry Pi. The accompanying [pibot](https://github.com/kafitz/pibot) 
project allows for reporting logbot updates to IRC. Logbot is designed to be an alternative
to scheduling many python scripts via cronjobs and to be able to be run portably.

#### Setup
1. To allow sqlalchemy and lxml c extensions to compile, first install:
```sudo apt-get install libxml2-dev libxslt1-dev python-dev```
2. Then run ```pip install -r requirements.txt``` to install rest of dependencies.
3. Logbot makes use of redis to pass messages to pibot: 
```sudo apt-get install redis-server```
4.  Run logbot with ```python logbot.py```  which can be run alongside pibot in separate ```screen``` instances.

#### Modules
Most modules in logbot both publish to redis and write data to an sqlite database for presistence. Logbot's modules include:
* arduino: Receives serial messages from an arduino plugged in by USB
* craigslist: Crawls first page of a craigslist search and notifies of new posts
* transitfeeds: Checks [api.transitfeeds.com](http://transitfeeds.com) for a new version of GTFS data and emails the address set in the config file if an update is found
* waterlevels: Checks [tides.gc.ca](http://tides.gc.ca/) once a day for river/tidal heights for a location (hardcoded in url) over the past 24 hours
* weather: Fetches the current conditions from [api.openweathermap.org](http://openweathermap.org)

#### Notes
Logbot currently uses the [dataset](https://dataset.readthedocs.org/en/latest/) wrapper which handy but slow to start on a Raspberry Pi (relies on sqlalchemy).
