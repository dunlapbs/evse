"""Switch platform for Grizzl-E."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchDeviceClass, SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import GrizzleConfigEntry
from .coordinator import GrizzleCoordinator
from .entity import GrizzleEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: GrizzleConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Grizzl-E switches."""
    coordinator = entry.runtime_data
    async_add_entities([GrizzleChargingSwitch(coordinator)])


class GrizzleChargingSwitch(GrizzleEntity, SwitchEntity):
    """Switch to enable/disable charging."""

    _attr_translation_key = "charging_enabled"
    _attr_device_class = SwitchDeviceClass.SWITCH
    _attr_icon = "mdi:ev-station"

    def __init__(self, coordinator: GrizzleCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{self._serial}_charging_enabled"

    @property
    def is_on(self) -> bool | None:
        val = self.coordinator.data.get("evseEnabled")
        if val is not None:
            return val == 0  # 0 = enabled (charging allowed), 1 = stopped
        return None

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Enable charging."""
        await self.coordinator.api.send_command("evseEnabled", 0)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Disable charging."""
        await self.coordinator.api.send_command("evseEnabled", 1)
        await self.coordinator.async_request_refresh()
