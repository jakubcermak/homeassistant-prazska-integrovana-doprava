"""The PID component."""


from __future__ import annotations
import json
import logging
import os

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .pid_connector import PidConnector

_LOGGER = logging.getLogger(__name__)


# List of platforms to support. There should be a matching .py file for each,
# eg <cover.py> and <sensor.py>
PLATFORMS: list[str] = ["sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})

    # Store an instance of the "connecting" class that does the work of speaking
    # with your actual devices.
    connector = PidConnector(entry.data[CONF_API_KEY])
    connector.set_stops(entry.data["stop_ids"])

    hass.data[DOMAIN][entry.entry_id] = connector

    # This creates each HA object for each platform your device requires.
    # It's done by calling the `async_setup_entry` function in each platform module.
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(update_listener))

    return True


async def update_listener(hass, entry):
    """Handle options update."""
    connector = hass.data[DOMAIN][entry.entry_id]
    connector.set_stops(entry.data["stop_ids"])


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # This is called when an entry/configured device is to be removed. The class
    # needs to unload itself, and remove callbacks. See the classes for further
    # details
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
