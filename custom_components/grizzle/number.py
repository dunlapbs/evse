"""Number platform for Grizzl-E."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.number import NumberDeviceClass, NumberEntity, NumberMode
from homeassistant.const import UnitOfElectricCurrent
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import GrizzleConfigEntry
from .const import CONF_COST_PER_KWH, DEFAULT_COST_PER_KWH
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
    async_add_entities([
        GrizzleCurrentLimit(coordinator),
        GrizzleCostPerKwh(coordinator, entry),
    ])


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


class GrizzleCostPerKwh(GrizzleEntity, NumberEntity):
    """Number entity to set the electricity cost per kWh."""

    _attr_translation_key = "cost_per_kwh"
    _attr_icon = "mdi:currency-usd"
    _attr_mode = NumberMode.BOX
    _attr_native_min_value = 0.0
    _attr_native_max_value = 1.0
    _attr_native_step = 0.01
    _attr_native_unit_of_measurement = "$/kWh"

    def __init__(self, coordinator: GrizzleCoordinator, entry: GrizzleConfigEntry) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{self._serial}_cost_per_kwh"

    @property
    def native_value(self) -> float:
        return self._entry.options.get(CONF_COST_PER_KWH, DEFAULT_COST_PER_KWH)

    async def async_set_native_value(self, value: float) -> None:
        """Update cost per kWh in config entry options."""
        new_options = {**self._entry.options, CONF_COST_PER_KWH: value}
        self.hass.config_entries.async_update_entry(self._entry, options=new_options)
        self.async_write_ha_state()
