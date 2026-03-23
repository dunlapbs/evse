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
    async_add_entities([
        GrizzleChargingSwitch(coordinator),
        GrizzleOcppSwitch(coordinator),
    ])


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
            return val == 0  # 0 = charging allowed, 1 = stop charging
        return None

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Enable charging."""
        await self.coordinator.api.send_command("evseEnabled", 0)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Disable charging."""
        await self.coordinator.api.send_command("evseEnabled", 1)
        await self.coordinator.async_request_refresh()


class GrizzleOcppSwitch(GrizzleEntity, SwitchEntity):
    """Switch to enable/disable OCPP cloud connection."""

    _attr_translation_key = "ocpp_cloud"
    _attr_icon = "mdi:cloud-outline"

    def __init__(self, coordinator: GrizzleCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{self._serial}_ocpp_cloud"

    @property
    def is_on(self) -> bool | None:
        val = self.coordinator.data.get("ocppEnabled")
        if val is not None:
            return val == 1
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Show OCPP connection status as an attribute."""
        connected = self.coordinator.data.get("ocppconnected")
        return {"cloud_connected": connected == 1 if connected is not None else None}

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Enable OCPP cloud."""
        await self.coordinator.api.send_ocpp_command("ocppEnabled", 1)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Disable OCPP cloud."""
        await self.coordinator.api.send_ocpp_command("ocppEnabled", 0)
        await self.coordinator.async_request_refresh()
