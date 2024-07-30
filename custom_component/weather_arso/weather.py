import logging
import voluptuous as vol
from homeassistant.components.weather import (
    PLATFORM_SCHEMA,
    WeatherEntity,
    WeatherEntityFeature,
)
from homeassistant.const import CONF_NAME
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .weather_arso import (
    get_arso_weather,
    get_arso_forecast_daily,
    get_arso_forecast_hourly,
    get_arso_forecast_twice_daily,
)

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME, default="ARSO Weather"): str,
})

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    name = config.get(CONF_NAME)
    station_id = "LJUBL-ANA_BEZIGRAD" 
    async_add_entities([ARSOWeather(hass, station_id, name)], True)

class ARSOWeather(WeatherEntity):
    _attr_supported_features = (
        WeatherEntityFeature.FORECAST_DAILY |
        WeatherEntityFeature.FORECAST_HOURLY |
        WeatherEntityFeature.FORECAST_TWICE_DAILY
    )

    def __init__(self, hass, station_id, name):
        self._station_id = station_id
        self._name = name
        self._state = None
        self._attributes = {}
        self._session = async_get_clientsession(hass)
        self._forecast_daily = None
        self._forecast_hourly = None
        self._forecast_twice_daily = None

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
        return "°C"

    @property
    def wind_speed_unit(self):
        return "m/s"

    @property
    def pressure_unit(self):
        return "mbar"

    @property
    def visibility(self):
        return self._attributes.get("visibility")

    @property
    def forecast(self):
        return self._forecast_daily

    async def async_update(self):
        """Fetch new state data for the sensor."""
        try:
            data = await self.hass.async_add_executor_job(get_arso_weather, self._station_id)
            if data:
                _LOGGER.debug(f"Fetched ARSO weather data: {data}")
                self._state = data.get("condition")
                self._attributes.update(data)
                
            self._forecast_daily = await self.hass.async_add_executor_job(get_arso_forecast_daily, self._station_id)
            self._forecast_hourly = await self.hass.async_add_executor_job(get_arso_forecast_hourly, self._station_id)
            self._forecast_twice_daily = await self.hass.async_add_executor_job(get_arso_forecast_twice_daily, self._station_id)
        except Exception as e:
            _LOGGER.error(f"Error fetching ARSO weather data: {e}")

    async def async_forecast_daily(self):
        return self._forecast_daily

    async def async_forecast_hourly(self):
        return self._forecast_hourly

    async def async_forecast_twice_daily(self):
        return self._forecast_twice_daily