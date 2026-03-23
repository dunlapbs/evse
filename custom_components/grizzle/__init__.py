"""The Grizzl-E EV Charger integration."""

from __future__ import annotations

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import GrizzleApi
from .coordinator import GrizzleCoordinator

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.SWITCH, Platform.NUMBER]

type GrizzleConfigEntry = ConfigEntry[GrizzleCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: GrizzleConfigEntry) -> bool:
    """Set up Grizzl-E from a config entry."""
    session = async_get_clientsession(hass)
    api = GrizzleApi(entry.data[CONF_HOST], session)

    coordinator = GrizzleCoordinator(hass, api)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: GrizzleConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
