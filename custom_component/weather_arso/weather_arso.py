import feedparser
import logging
from datetime import datetime

_LOGGER = logging.getLogger(__name__)

CONDITION_MAP = {
    "Jasno.": "sunny",
    "Pretežno jasno.": "sunny",
    "Delno oblačno.": "partlycloudy",
    "Oblačno.": "cloudy",
    "Megleno.": "fog",
    "Močni nalivi.": "pouring",
    "Deževno.": "rainy",
    "Nevihte z dežjem.": "lightning-rainy",
    "Snežilo.": "snowy",
    "Mešanica snega in dežja.": "snowy-rainy",
    "Veter.": "windy",
    "Vihar.": "windy-variant",
    "Izjemno vreme.": "exceptional",
    # Add other mappings as necessary
}

WIND_BEARINGS = {
    "Z": "W",
    "S": "N",
    "V": "E",
    "J": "S",
    "SV": "NE",
    "SZ": "NW",
    "JV": "SE",
    "JZ": "SW",
    # Add other mappings as necessary
}

def get_arso_weather(station_id="LJUBL-ANA_BEZIGRAD"):
    url = f"https://meteo.arso.gov.si/uploads/probase/www/observ/surface/text/sl/observation_{station_id}_latest.rss"

    try:
        feed = feedparser.parse(url)
    except Exception as e:
        _LOGGER.error(f"Error fetching ARSO RSS data: {e}")
        return None

    if not feed.entries:
        _LOGGER.error("No entries found in ARSO RSS feed")
        return None

    entry = feed.entries[0]

    data = {
        "temperature": _extract_temperature(entry.summary),
        "condition": _extract_condition(entry.summary),
        "humidity": _extract_humidity(entry.summary),
        "wind_speed": _extract_wind_speed(entry.summary),
        "wind_bearing": _extract_wind_bearing(entry.summary),
        "pressure": _extract_pressure(entry.summary),
        "visibility": _extract_visibility(entry.summary),
        "native_dew_point": _extract_dew_point(entry.summary),
        "updated_at": datetime.now().isoformat(),
    }

    return data

def _extract_temperature(summary):
    try:
        _LOGGER.debug(f"Extracting temperature from summary: {summary}")
        start_index = summary.index("Temperatura: ") + len("Temperatura: ")
        end_index = summary.index("°C", start_index)
        temperature_str = summary[start_index:end_index].strip()
        temperature = float(temperature_str)
        _LOGGER.debug(f"Extracted temperature: {temperature}")
        return temperature
    except (ValueError, IndexError):
        try:
            _LOGGER.debug(f"Trying to extract dew point temperature from summary: {summary}")
            start_index = summary.index("Temperatura rosišča: ") + len("Temperatura rosišča: ")
            end_index = summary.index("°C", start_index)
            dew_point_str = summary[start_index:end_index].strip()
            dew_point = float(dew_point_str)
            _LOGGER.debug(f"Extracted dew point temperature: {dew_point}")
            return dew_point
        except (ValueError, IndexError) as e:
            _LOGGER.error(f"Error extracting temperature: {e}, summary: {summary}")
            return None

def _extract_condition(summary):
    try:
        _LOGGER.debug(f"Extracting condition from summary: {summary}")
        for key in CONDITION_MAP:
            if key in summary:
                condition = CONDITION_MAP[key]
                _LOGGER.debug(f"Extracted condition: {condition}")
                return condition
        _LOGGER.debug(f"No condition found, returning None for summary: {summary}")
        return None
    except (ValueError, IndexError) as e:
        _LOGGER.error(f"Error extracting condition: {e}, summary: {summary}")
        return None

def _extract_humidity(summary):
    try:
        _LOGGER.debug(f"Extracting humidity from summary: {summary}")
        start_index = summary.index("Vlažnost zraka: ") + len("Vlažnost zraka: ")
        end_index = summary.index("%", start_index)
        humidity = int(summary[start_index:end_index].strip())
        _LOGGER.debug(f"Extracted humidity: {humidity}")
        return humidity
    except (ValueError, IndexError) as e:
        _LOGGER.error(f"Error extracting humidity: {e}, summary: {summary}")
        return None

def _extract_wind_speed(summary):
    try:
        _LOGGER.debug(f"Extracting wind speed from summary: {summary}")
        start_index = summary.index(": ", summary.index("Piha ")) + 2
        end_index = summary.index(" m/s", start_index)
        wind_speed = float(summary[start_index:end_index].strip().split(" ")[0])
        _LOGGER.debug(f"Extracted wind speed: {wind_speed}")
        return wind_speed
    except (ValueError, IndexError) as e:
        _LOGGER.error(f"Error extracting wind speed: {e}, summary: {summary}")
        return None

def _extract_wind_bearing(summary):
    try:
        _LOGGER.debug(f"Extracting wind bearing from summary: {summary}")
        start_index = summary.index("Piha ") + len("Piha ")
        end_index = summary.index(":", start_index)
        wind_bearing = summary[start_index:end_index].strip().split(" ")[-1].replace("(", "").replace(")", "")
        wind_bearing_translated = WIND_BEARINGS.get(wind_bearing, wind_bearing)
        _LOGGER.debug(f"Extracted wind bearing: {wind_bearing_translated}")
        return wind_bearing_translated
    except (ValueError, IndexError) as e:
        _LOGGER.error(f"Error extracting wind bearing: {e}, summary: {summary}")
        return None

def _extract_pressure(summary):
    try:
        _LOGGER.debug(f"Extracting pressure from summary: {summary}")
        start_index = summary.index("Zračni tlak: ") + len("Zračni tlak: ")
        end_index = summary.index(" mbar", start_index)
        pressure = int(summary[start_index:end_index].strip().split(" ")[0])
        _LOGGER.debug(f"Extracted pressure: {pressure}")
        return pressure
    except (ValueError, IndexError) as e:
        _LOGGER.error(f"Error extracting pressure: {e}, summary: {summary}")
        return None

def _extract_visibility(summary):
    try:
        _LOGGER.debug(f"Extracting visibility from summary: {summary}")
        start_index = summary.index("Vidnost: ") + len("Vidnost: ")
        end_index = summary.index(" km", start_index)
        visibility = float(summary[start_index:end_index].strip())
        _LOGGER.debug(f"Extracted visibility: {visibility}")
        return visibility
    except (ValueError, IndexError) as e:
        _LOGGER.error(f"Error extracting visibility: {e}, summary: {summary}")
        return None

def _extract_dew_point(summary):
    try:
        _LOGGER.debug(f"Extracting dew point from summary: {summary}")
        start_index = summary.index("Temperatura rosišča: ") + len("Temperatura rosišča: ")
        end_index = summary.index("°C", start_index)
        dew_point = float(summary[start_index:end_index].strip())
        _LOGGER.debug(f"Extracted dew point: {dew_point}")
        return dew_point
    except (ValueError, IndexError) as e:
        _LOGGER.error(f"Error extracting dew point: {e}, summary: {summary}")
        return None

def get_arso_forecast_daily(station_id="LJUBL-ANA_BEZIGRAD"):
    url = "https://meteo.arso.gov.si/uploads/probase/www/fproduct/text/sl/fcast_SI_OSREDNJESLOVENSKA_latest.rss"

    try:
        feed = feedparser.parse(url)
    except Exception as e:
        _LOGGER.error(f"Error fetching ARSO RSS forecast data: {e}")
        return None

    if not feed.entries:
        _LOGGER.error("No entries found in ARSO RSS forecast feed")
        return None

    forecasts = []
    for entry in feed.entries:
        forecast = _parse_forecast_entry(entry)
        if forecast:
            forecasts.append(forecast)

    return forecasts

def _parse_forecast_entry(entry):
    try:
        forecast = {
            "datetime": datetime(*entry.published_parsed[:6]).isoformat(),
            "native_temperature": _extract_float(entry.summary, "max temperature: ", "°C"),
            "native_templow": _extract_float(entry.summary, "min temperature: ", "°C"),
            "condition": _extract_condition(entry.summary),
            # Add more fields as necessary
        }
        return forecast
    except (ValueError, IndexError) as e:
        _LOGGER.error(f"Error parsing forecast entry: {e}")
        return None

def _extract_float(text, prefix, suffix):
    try:
        start_index = text.index(prefix) + len(prefix)
        end_index = text.index(suffix, start_index)
        return float(text[start_index:end_index].strip())
    except (ValueError, IndexError):
        return None

def get_arso_forecast_hourly(station_id="LJUBL-ANA_BEZIGRAD"):
    # Implement similarly to daily forecast by fetching hourly data
    pass

def get_arso_forecast_twice_daily(station_id="LJUBL-ANA_BEZIGRAD"):
    # Implement similarly to daily forecast by fetching twice daily data
    pass