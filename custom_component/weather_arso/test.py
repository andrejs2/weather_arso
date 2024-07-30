import feedparser

url = "https://meteo.arso.gov.si/uploads/probase/www/observ/surface/text/sl/observation_LJUBL-ANA_BEZIGRAD_latest.rss"
feed = feedparser.parse(url)

print(feed)