import datetime
import logging
import json
import os

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import DEVICE_CLASS_TIMESTAMP
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .pid_connector import PidConnection, PidConnector

_LOGGER = logging.getLogger(__name__)


# This function is called as part of the __init__.async_setup_entry (via the
# hass.config_entries.async_forward_entry_setup call)
async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add cover for passed config_entry in HA."""
    # The hub is loaded from the associated hass.data entry that was created in the
    # __init__.async_setup_entry function
    connector = hass.data[DOMAIN][config_entry.entry_id]

    # Add all entities to HA
    async_add_entities(TimeTableSensor(connector, i) for i in [0, 1, 2, 3, 4])


class TimeTableSensor(SensorEntity):
    _data: list[PidConnection] = []

    def __init__(self, connector: PidConnector, n: int) -> None:
        self._connector = connector
        self._n = n
        self._has_data = False
        _LOGGER.debug("component %s created", n)

    device_class = DEVICE_CLASS_TIMESTAMP

    @property
    def unique_id(self) -> str | None:
        return f"pid_departure_{self._n+1}"

    @property
    def name(self) -> str | None:
        return f"PID Odjezd {self._n+1}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""
        return DeviceInfo(
            identifiers={
                # Serial numbers are unique identifiers within a specific domain
                (DOMAIN, "departures")
            },
            name="PID Odjezdy",
            sw_version=1,
        )

    @property
    def available(self) -> bool:
        return self._has_data and len(self._data) > self._n

    def update(self) -> None:
        stops_data_file_location = self.hass.config.path("pid_stops_list.json")
        if not os.path.exists(stops_data_file_location):
            _LOGGER.info("Downloading stops data file to %s", stops_data_file_location)
            stops = self._connector.get_stops()
            j = json.dumps(stops)
            with open(stops_data_file_location, "wt", encoding="utf-8") as file:
                file.write(j)
            _LOGGER.debug("download ok")

        self._data = self._connector.get_timetable()
        self._has_data = True

    @property
    def native_value(self) -> datetime:
        if self.available:
            return (
                self._data[self._n].predicted
                if self._data[self._n].delay_available
                else self._data[self._n].scheduled
            )
        else:
            return None

    @property
    def extra_state_attributes(self) -> dict[str, str]:
        l = self._data[self._n]
        return (
            {
                "stop_from": l.stop_from,
                "stop_to": l.stop_to,
                "scheduled": l.scheduled,
                "predicted": l.predicted,
                "delay_available": l.delay_available,
                "linenumber": l.linenumber,
                "details": f"{l.linenumber}: {l.stop_from} -> {l.stop_to}",
            }
            if self.available
            else {}
        )
