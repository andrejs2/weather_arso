import requests
import feedparser
import re

# Function to fetch RSS feed content
def fetch_rss_feed(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.content

# Function to parse RSS feed content
def parse_rss_feed(feed_content):
    feed = feedparser.parse(feed_content)
    return feed

# Function to extract data using regex patterns
def extract_from_text(pattern, text, flags=re.IGNORECASE):
    match = re.search(pattern, text, flags)
    if match:
        return match.group(1)
    return None

# Mapping from Slovenian weather conditions to English terms
weather_condition_map = {
    "pretežno jasno": "sunny",
    "jasno": "sunny",
    "delno oblačno": "partlycloudy",
    "pretežno oblačno": "cloudy",
    "oblačno": "cloudy",
    "megla": "fog",
    "megleno": "fog",
    "dež": "rainy",
    "deževno": "rainy",
    "plohe": "pouring",
    "nevihte": "lightning-rainy",
    "sneženje": "snowy",
    "snežna ploha": "snowy-rainy",
    "toča": "hail",
    "izjemno": "exceptional",
}

# Function to extract weather details from an RSS feed entry
def extract_weather_details(entry):
    details = {}

    # Patterns to extract weather data
    patterns = {
        'temperature': r'(\d+)\s*°C',
        'wind_bearing': r'Piha\s.*\((\w+)\):',
        'wind_speed': r'Piha\s.*\(\w+\):\s(\d+)\sm/s',
        'native_visibility': r'Vidnost:\s*(\d+)\s*km',
        'native_visibility_unit': r'Vidnost:\s*\d+\s*(km)',
        'native_pressure': r'Zračni tlak:\s*(\d+)\s*mbar',
        'native_pressure_unit': r'Zračni tlak:\s*\d+\s*(mbar)',
        'native_dew_point': r'Temperatura rosišča:\s*(\d+)\s*°C',
        'humidity': r'Vlažnost zraka:\s*(\d+)\s*%'
    }

    combined_text = f"{entry.title} {entry.summary}"

    for key, pattern in patterns.items():
        details[key] = extract_from_text(pattern, combined_text)

    # Extract weather condition from title
    weather_condition_slovenian = extract_from_text(r':\s*(.*?),\s*\d+\s*°C', entry.title)
    if weather_condition_slovenian:
        details['condition'] = weather_condition_map.get(weather_condition_slovenian.lower(), weather_condition_slovenian)

    # Special handling for wind bearing mappings
    wind_bearing_map = {
        'JZ': 'SW', 'JV': 'SE', 'SZ': 'NW', 'SV': 'NE',
        'J': 'S', 'Z': 'W', 'S': 'N', 'V': 'E'
    }
    if 'wind_bearing' in details:
        details['wind_bearing'] = wind_bearing_map.get(details['wind_bearing'], details['wind_bearing'])

    return details

def main():
    rss_url = 'https://meteo.arso.gov.si/uploads/probase/www/observ/surface/text/sl/observation_LJUBL-ANA_BEZIGRAD_latest.rss'

    # Fetch RSS feed content
    feed_content = fetch_rss_feed(rss_url)

    # Parse RSS feed
    feed = parse_rss_feed(feed_content)
    
    # Process each entry in feed
    for entry in feed.entries:
        print(f"Title: {entry.title}")

        # Extract weather details
        details = extract_weather_details(entry)
        
        # Print extracted details
        for key, value in details.items():
            if value is not None:
                print(f"{key}: {value}")

        print()  # Print a newline for separation between entries

if __name__ == "__main__":
    main()