import feedparser
from flask import Flask
from flask import render_template
from flask import request
import json
import urllib
import urllib2

app = Flask(__name__)

proxy = urllib2.ProxyHandler( {"http":"http://adc-proxy.oracle.com:80/", "https:":"http://adc-proxy.oracle.com:80/"} )
opener = urllib2.build_opener(proxy)
urllib2.install_opener(opener)

RSS_FEEDS = { 'bbc': 'http://feeds.bbci.co.uk/news/rss.xml',
              'cnn': 'http://rss.cnn.com/rss/edition.rss',
              'fox': 'http://feeds.foxnews.com/foxnews/latest',
              'iol': 'http://rss.iol.io/iol/news' }

WEATHER_URL = 'http://api.openweathermap.org/data/2.5/weather?q={}units=metric&APPID=b6b29fb31b6ac7ce903f3773cd2e8484'

DEFAULTS = {'publication':'bbc',
            'city': 'London,UK'}
               
@app.route("/")
def home():
    # get customized headlines, based on user input or default 
    publication = request.args.get('publication')
    if not publication:
        publication = DEFAULTS['publication']
    articles =  get_news(publication)
    # get customized weather based on user input or default
    city = request.args.get('city')
    if not city:
        city = DEFAULTS['city']
    print 'city is: %s' % city
    weather = get_weather(city)
    return render_template("home.html", articles=articles, weather=weather)

def get_news(publication):
    feed = feedparser.parse(RSS_FEEDS[publication], handlers = [proxy])
    return feed['entries']


def get_weather(query):
    query = urllib.quote(query)
    url = WEATHER_URL.format(query)
    data = urllib2.urlopen(url).read()
    parsed = json.loads(data)
    weather = None
    if parsed.get('weather'):
        weather = {'description':parsed['weather'][0]['description'],
                   'temperature':parsed['main']['temp'],
                   'city':parsed['name'],
                   'country': parsed['sys']['country']
                  }
    return weather

if __name__ == '__main__':
    app.run(port=5000, debug=True)
