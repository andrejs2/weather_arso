import logging
import asyncio
import re
import requests
import feedparser
from datetime import datetime

from homeassistant.components.weather import (
    PLATFORM_SCHEMA as PARENT_PLATFORM_SCHEMA,
    WeatherEntity,
)
from homeassistant.const import (
    CONF_NAME,
)
import voluptuous as vol  
from homeassistant.util.unit_system import UnitOfTemperature 


_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PARENT_PLATFORM_SCHEMA.extend(
    {
        vol.Optional(CONF_NAME): str,
    }
)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the ARSO weather platform."""
    name = config.get(CONF_NAME)
    station_id = config.get("station_id", "LJUBL-ANA_BEZIGRAD")
    async_add_entities([ARSOWeather(hass, station_id, name)])


class ARSOWeather(WeatherEntity):
    def __init__(self, hass, station_id, name=None):
        self._hass = hass
        self._station_id = station_id
        self._name = name or f"ARSO Weather ({station_id})"
        self._state = None
        self._attributes = {}

    @property
    def name(self):
        return self._name

    @property
    def temperature(self):
        return self._attributes.get("temperature")

    @property
    def humidity(self):
        return self._attributes.get("humidity")

    @property
    def wind_speed(self):
        return self._attributes.get("wind_speed")

    @property
    def wind_bearing(self):
        return self._attributes.get("wind_bearing")

    @property
    def pressure(self):
        return self._attributes.get("pressure")

    @property
    def condition(self):
        return self._attributes.get("condition")

    @property
    def temperature_unit(self):
        return UnitOfTemperature.CELSIUS
   
   # Additional properties for wind_speed_unit, pressure_unit etc...
   
    @property
    def wind_speed_unit(self):
        """Return the unit of measurement for wind speed."""
        return "km/h"

    @property
    def pressure_unit(self):
        """Return the unit of measurement for pressure."""
        return "hPa"

    @property
    def visibility_unit(self):
        """Return the unit of measurement for visibility."""
        return "km"

    @property
    def attribution(self):
        """Return the attribution."""
        return "Data provided by ARSO"

    async def async_update(self): # Update function should be async
        """Fetch new state data for the sensor."""
        _LOGGER.info("Updating ARSO weather information for %s", self._name)
        try:
            self._attributes = await self._hass.async_add_executor_job(
                self._get_arso_weather
            )
        except Exception as e:
            _LOGGER.error(f"Error fetching ARSO weather data: {e}")
            return None

    def _get_arso_weather(self):
        url = f"https://meteo.arso.gov.si/uploads/probase/www/observ/surface/text/sl/observation_{self._station_id}_latest.rss"

        try:
            feed = feedparser.parse(url)
        except Exception as e:
            _LOGGER.error(f"Error fetching ARSO RSS data: {e}")
            return None

        if not feed.entries:
            _LOGGER.error("No entries found in ARSO RSS feed")
            return None

        entry = feed.entries[0]  # Get the latest entry
        summary = entry.summary.split("<br />")[1].strip()  # Extract the relevant part of the summary

        data = {
            "temperature": self._extract_temperature(entry.title),
            "condition": self._extract_condition(entry.summary),
            "humidity": self._extract_humidity(summary),
            "wind_speed": self._extract_wind_speed(summary),
            "wind_bearing": self._extract_wind_bearing(summary),
            "pressure": self._extract_pressure(summary),
            "updated_at": self._extract_updated_at(entry.title),
            # Add new attributes
            "cloud_coverage": 0,  # Assuming clear sky based on "Jasno" condition
            "dew_point": self._extract_dew_point(summary),
            "visibility": self._extract_visibility(summary),
            "wind_gust_speed": self._extract_wind_gust(summary),
            "uv_index": None,       # Not available in the RSS feed
        }

        return data


    # Helper functions to extract data from the RSS summary
    def _extract_temperature(self, title):
        match = re.search(r'(\d+)\s*°C', title) #extract temperature using re
        if match:
            return int(match.group(1))
        return None
        
    def _extract_condition(self, summary):
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

    def _extract_humidity(self, summary):
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

    def _extract_wind_speed(self, summary):
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

    def _extract_wind_bearing(self, summary):
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

    def _extract_pressure(self, summary):
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
