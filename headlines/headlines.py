import feedparser
from flask import Flask
from flask import render_template
from flask import request

import json
import urllib

import datetime
from flask import make_response

app = Flask(__name__)

RSS_FEEDS = {'bbc': 'https://feeds.bbci.co.uk/news/rss.xml',
             'cnn': 'http://rss.cnn.com/rss/edition.rss',
             'fox': 'http://feeds.foxnews.com/foxnews/latest',
             'iol': 'http://www.iol.co.za/cmlink/1.640'}

DEFAULTS = {'publication': 'cnn',
            'city': 'London,UK',
            'currency_from': 'GBP',
            'currency_to': 'USD'}

WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=66510e7a57bdfe190d0f5e3401be7bf2"
CURRENCY_URL = "https://openexchangerates.org/api/latest.json?app_id=4f16346d6f064243a320f36fad37c804"


@app.route("/")
# @app.route("/<publication>")
# def bbc():
#     return (get_news('bbc'))
# @app.route("/cnn")
# def cnn():
#     return (get_news('cnn'))
# def get_news(publication="cnn"):
#     feed = feedparser.parse(RSS_FEEDS[publication])
#     # first_article = feed['entries'][0]
#     """ URL routing with Flask """
#     # return ("""<html>
#     #             <body>
#     #                 <h1> Headlines </h1>
#     #                 <b>{0}</b> <br/>
#     #                 <i>{1}</i> <br/>
#     #                 <p>{2}</p> <br/>
#     #             </body>
#     #         </html>""".format(first_article.get("title"),
#     #                           first_article.get("published"),
#     #                           first_article.get("summary"))
#     #         )
#     """ Rendering basic template """
#     # return render_template("home.html")
#     """ Passing dynamic data to template """
#     # return render_template("home.html",
#     #                         title=first_article.get("title"),
#     #                         published=first_article.get("published"),
#     #                         summary=first_article.get("summary"))
#     """ Using Jinja objects """
#     # return render_template("home.html", article=first_article)
#     """ Adding looping """
#     return render_template("home.html", articles=feed['entries'])
### Getting user input using HTTP GET ###
# def get_news():
#     query = request.args.get("publication")
#     if not query or query.lower() not in RSS_FEEDS:
#         publication = "cnn"
#     else:
#         publication = query.lower()
#     feed = feedparser.parse(RSS_FEEDS[publication])
#     return render_template("home.html", articles=feed['entries'])
def home():
    # get customized headlines, based on user input or default
    # publication = request.args.get('publication')
    # if not publication:
    #     publication = request.cookies.get('publication')
    #     if not publication:
    #         publication = DEFAULTS['publication']
    publication = get_value_with_fallback("publication")
    articles = get_news(publication)

    # get customized weather based on user input or default
    # city = request.args.get('city')
    # if not city:
    #     city = DEFAULTS['city']
    # weather = get_weather(city)
    city = get_value_with_fallback("city")
    weather = get_weather(city)

    # get customized currency based on user input or default
    # currency_from = request.args.get('currency_from')
    # if not currency_from:
    #     currency_from = DEFAULTS['currency_from']

    # currency_to = request.args.get('currency_to')
    # if not currency_to:
    #     currency_to = DEFAULTS['currency_to']

    # rate, currencies = get_rate(currency_from, currency_to)
    currency_from = get_value_with_fallback("currency_from")
    currency_to = get_value_with_fallback("currency_to")
    rate, currencies = get_rate(currency_from, currency_to)

    """ save cookies and return template """
    response = make_response(render_template("home.html",
                                             articles=articles,
                                             weather=weather,
                                             currency_from=currency_from,
                                             currency_to=currency_to,
                                             rate=rate,
                                             currencies=sorted(currencies)))

    expires = datetime.datetime.now() + datetime.timedelta(days=365)

    response.set_cookie("publication", publication, expires=expires)
    response.set_cookie("city", city, expires=expires)
    response.set_cookie("currency_from", currency_from, expires=expires)
    response.set_cookie("currency_to", currency_to, expires=expires)

    return response


def get_news(query):
    if not query or query.lower() not in RSS_FEEDS:
        publication = DEFAULTS["publication"]
    else:
        publication = query.lower()

    feed = feedparser.parse(RSS_FEEDS[publication])
    return (feed['entries'])


def get_weather(query):
    query = urllib.parse.quote(query)
    url = WEATHER_URL.format(query)
    data = urllib.request.urlopen(url).read()
    parsed = json.loads(data)
    weather = None
    if parsed.get('weather'):
        weather = {'description': parsed['weather'][0]['description'],
                   'temperature': parsed['main']['temp'],
                   'city': parsed['name']}

    return (weather)


def get_rate(frm, to):
    all_currency = urllib.request.urlopen(CURRENCY_URL).read()
    parsed = json.loads(all_currency).get('rates')
    frm_rate = parsed.get(frm.upper())
    to_rate = parsed.get(to.upper())

    return (to_rate/frm_rate, parsed.keys())


def get_value_with_fallback(key):
    if request.args.get(key):
        return request.args.get(key)
    if request.cookies.get(key):
        return request.cookies.get(key)
    return DEFAULTS[key]


if __name__ == '__main__':
    app.run(port=5000, debug=True)
