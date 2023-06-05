import datetime
import logging

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

    def __init__(self, connector: PidConnector, n: int):
        self._connector = connector
        self._n = n
        self._has_data = False
        _LOGGER.debug(f"component {n} created")

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
        self._data = self._connector.get_timetable()
        self._has_data = True

    @property
    def native_value(self) -> datetime:
        return self._data[self._n].scheduled if self.available else None