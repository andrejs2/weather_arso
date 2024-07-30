import requests
import feedparser
import re

def fetch_rss_feed(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.content

def parse_rss_feed(feed_content):
    feed = feedparser.parse(feed_content)
    return feed

def extract_temperature_from_title(title):
    match = re.search(r'(\d+)\s*°C', title)
    if match:
        return int(match.group(1))
    return None

def main():
    rss_url = 'https://meteo.arso.gov.si/uploads/probase/www/observ/surface/text/sl/observation_LJUBL-ANA_BEZIGRAD_latest.rss'
    
    # Fetch RSS feed
    feed_content = fetch_rss_feed(rss_url)
    
    # Parse RSS feed
    feed = parse_rss_feed(feed_content)
    
    # Loop through entries in the RSS feed
    for entry in feed.entries:
        title = entry.title
        print(f"Title: {title}")
        
        # Extract temperature from title
        temperature = extract_temperature_from_title(title)
        if temperature is not None:
            print(f"Extracted Temperature: {temperature}°C")
        else:
            print("Temperature not found in title.")

if __name__ == "__main__":
    main()