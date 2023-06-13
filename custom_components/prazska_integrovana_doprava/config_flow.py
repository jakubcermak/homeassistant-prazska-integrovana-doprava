"""Config flow for PID integration."""
from __future__ import annotations

import logging
from typing import Any

# from homeassistant.helpers.aiohttp_client import async_get_clientsession
import voluptuous as vol
from .pid_connector import PidConnector, PidException

from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY, CONF_SCAN_INTERVAL
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN

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


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class NotSupported(HomeAssistantError):
    """Error to indicate we cannot connect."""
