"""Number platform for Grizzl-E."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.number import NumberDeviceClass, NumberEntity, NumberMode
from homeassistant.const import UnitOfElectricCurrent
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
    """Set up Grizzl-E number entities."""
    coordinator = entry.runtime_data
    async_add_entities([GrizzleCurrentLimit(coordinator)])


class GrizzleCurrentLimit(GrizzleEntity, NumberEntity):
    """Number entity to set the charging current limit."""

    _attr_translation_key = "current_limit_set"
    _attr_device_class = NumberDeviceClass.CURRENT
    _attr_native_unit_of_measurement = UnitOfElectricCurrent.AMPERE
    _attr_mode = NumberMode.SLIDER
    _attr_icon = "mdi:current-ac"

    def __init__(self, coordinator: GrizzleCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{self._serial}_current_limit_set"
        self._attr_native_min_value = float(
            coordinator.data.get("minCurrent", 7)
        )
        self._attr_native_max_value = float(
            coordinator.data.get("curDesign", 48)
        )
        self._attr_native_step = 1.0

    @property
    def native_value(self) -> float | None:
        val = self.coordinator.data.get("currentSet")
        return float(val) if val is not None else None

    async def async_set_native_value(self, value: float) -> None:
        """Set the current limit."""
        await self.coordinator.api.send_command("currentSet", int(value))
        await self.coordinator.async_request_refresh()
