"""Config flow for Grizzl-E."""

from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.const import CONF_HOST
from homeassistant.core import callback

from .api import GrizzleApi, GrizzleConnectionError
from .const import CONF_COST_PER_KWH, DEFAULT_COST_PER_KWH, DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
    }
)


class GrizzleConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Grizzl-E."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST]

            try:
                session = aiohttp.ClientSession()
                api = GrizzleApi(host, session)
                data = await api.async_validate_connection()
                await session.close()
            except GrizzleConnectionError:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                serial = data.get("serialNum", host)
                await self.async_set_unique_id(serial)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"Grizzl-E {serial}",
                    data={CONF_HOST: host},
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow."""
        return GrizzleOptionsFlow(config_entry)


class GrizzleOptionsFlow(OptionsFlow):
    """Handle options for Grizzl-E."""

    def __init__(self, config_entry) -> None:
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current_cost = self.config_entry.options.get(
            CONF_COST_PER_KWH, DEFAULT_COST_PER_KWH
        )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_COST_PER_KWH, default=current_cost): vol.Coerce(
                        float
                    ),
                }
            ),
        )
