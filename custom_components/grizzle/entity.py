"""Base entity for Grizzl-E."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER
from .coordinator import GrizzleCoordinator


class GrizzleEntity(CoordinatorEntity[GrizzleCoordinator]):
    """Base class for Grizzl-E entities."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: GrizzleCoordinator) -> None:
        super().__init__(coordinator)
        serial = coordinator.data.get("serialNum", "unknown")
        model = coordinator.data.get("model", "Grizzl-E")
        fw_main = coordinator.data.get("verFWMain", "").strip()
        fw_wifi = coordinator.data.get("verFWWifi", "").strip()
        sw_version = f"{fw_main} / {fw_wifi}" if fw_main else None

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, serial)},
            name=f"Grizzl-E {serial}",
            manufacturer=MANUFACTURER,
            model=model,
            serial_number=serial,
            sw_version=sw_version,
        )
        self._serial = serial
