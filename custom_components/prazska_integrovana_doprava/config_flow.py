"""Config flow for PID integration."""
from __future__ import annotations
import json

import logging
from typing import Any

# from homeassistant.helpers.aiohttp_client import async_get_clientsession
import voluptuous as vol

from homeassistant.core import callback
from .pid_connector import PidConnector, PidException

from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY, CONF_SCAN_INTERVAL
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN, CONF_STOP_ALL

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {vol.Required(CONF_API_KEY): str, vol.Optional(CONF_SCAN_INTERVAL, default=1): int}
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for PID."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        # user entered the config, let's verify
        errors = {}
        try:
            connector = PidConnector(user_input[CONF_API_KEY])
            connector.get_stops()

            _LOGGER.info("Initial request to Golemio API OK")

            return self.async_create_entry(
                title="Pražská integrovaná doprava", data=user_input
            )
        except PidException:
            errors["base"] = "cannot_connect"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return OptionsFlowHandler(config_entry)


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class NotSupported(HomeAssistantError):
    """Error to indicate we cannot connect."""


class OptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    def load_datafile(self):
        stops_data_file_location = self.hass.config.path("pid_stops_list.json")
        with open(stops_data_file_location, "rt", encoding="utf-8") as file:
            json_data = json.load(file)
        return json_data

    def validate_stopname(self, name: str) -> bool:
        json_data = self.load_datafile()
        return name in json_data.keys()

    def get_stopid(self, name: str) -> list[str]:
        json_data = self.load_datafile()
        return json_data[name]

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""

        OPTIONS_DATA_SCHEMA = vol.Schema(
            {
                vol.Optional(i, default=self.config_entry.options[i]): str
                for i in CONF_STOP_ALL
            }
        )

        if user_input is not None:
            errors = {}
            valid = True
            # uživatel potvrdil, zvalidujeme
            for cfg in CONF_STOP_ALL:
                if not not user_input[cfg]:
                    if not self.validate_stopname(user_input[cfg]):
                        errors["base"] = "unknown_stop_" + cfg
                        valid = False
                    else:
                        _LOGGER.debug("Stop %s %s is OK", cfg, user_input[cfg])
            if valid:
                stopids = []
                for cfg in CONF_STOP_ALL:
                    if user_input[cfg]:
                        stopids.extend(self.get_stopid(user_input[cfg]))
                _LOGGER.info("Configured to retrieve following stop IDs: %s", stopids)
                d = dict(self.config_entry.data)
                d.update({"stop_ids": stopids})
                self.hass.config_entries.async_update_entry(self.config_entry, data=d)
                return self.async_create_entry(title="", data=user_input)
            else:
                return self.async_show_form(
                    step_id="init", data_schema=OPTIONS_DATA_SCHEMA, errors=errors
                )

        return self.async_show_form(
            step_id="init",
            data_schema=OPTIONS_DATA_SCHEMA,
        )
