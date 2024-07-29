"""The ARSO Weather component."""
from homeassistant.helpers import discovery

DOMAIN = "weather_arso"

async def async_setup(hass, config):
    """Set up the ARSO weather component."""
    await discovery.async_load_platform(hass, "weather", DOMAIN, {}, config)
    return True

async def async_setup_entry(hass, config_entry):
    """Set up the ARSO weather component from a config entry."""
    hass.async_create_task(hass.config_entries.async_forward_entry_setup(config_entry, "weather"))
    return True