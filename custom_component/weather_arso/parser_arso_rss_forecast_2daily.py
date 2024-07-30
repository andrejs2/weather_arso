import feedparser
import re

# URL of the RSS feed
rss_url = 'https://meteo.arso.gov.si/uploads/probase/www/fproduct/text/sl/fcast_SI_OSREDNJESLOVENSKA_latest.rss'

# Parse the RSS feed
feed = feedparser.parse(rss_url)

# Regular expressions to parse the weather details
condition_re = re.compile(r'(\bjasno\b|\boblačno\b|\bdež\b|\bsneg\b|\bsparno\b|\bpadavine\b|[\w\s]+)')
temperature_re = re.compile(r'([-+]?\d*\.?\d+)\s*°C')
wind_re = re.compile(r'\b(vzhodni veter|severni veter|južni veter|zahodni veter|[\w\s]+)\b')
wind_speed_re = re.compile(r'(\d+\s*\.\s*\d+|\d+)\s*m/s')

# Function to extract weather details from the description
def extract_weather_details(description):
    condition = condition_re.search(description)
    temperature = temperature_re.search(description)
    wind = wind_re.search(description)
    wind_speed = wind_speed_re.search(description)

    return {
        'condition': condition.group(0) if condition else 'N/A',
        'temperature': temperature.group(1) if temperature else 'N/A',
        'wind': wind.group(0) if wind else 'N/A',
        'wind_speed': wind_speed.group(1) if wind_speed else 'N/A'
    }

# Check if the feed was parsed correctly
if 'entries' in feed:
    # Loop through the feed entries
    for entry in feed.entries:
        details = extract_weather_details(entry.description)
        print(f"Title: {entry.title}")
        print(f"Condition: {details['condition']}")
        print(f"Temperature: {details['temperature']} °C")
        print(f"Wind: {details['wind']}")
        print(f"Wind Speed: {details['wind_speed']} m/s")
        print('-' * 40)
else:
    print("Failed to retrieve the RSS feed.")