"""Sensor platform for Grizzl-E."""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import GrizzleConfigEntry
from .const import CHARGER_ERRORS, CHARGER_STATES, PILOT_STATES
from .coordinator import GrizzleCoordinator
from .entity import GrizzleEntity

SENSOR_DESCRIPTIONS: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key="voltMeas1",
        translation_key="voltage",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
    ),
    SensorEntityDescription(
        key="curMeas1",
        translation_key="current",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    SensorEntityDescription(
        key="powerMeas",
        translation_key="power",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=0,
    ),
    SensorEntityDescription(
        key="sessionEnergy",
        translation_key="session_energy",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL,
        suggested_display_precision=2,
    ),
    SensorEntityDescription(
        key="totalEnergy",
        translation_key="total_energy",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=1,
    ),
    SensorEntityDescription(
        key="sessionTime",
        translation_key="session_time",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="temperature1",
        translation_key="relay_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="temperature2",
        translation_key="plug_temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="currentSet",
        translation_key="current_limit",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="sessionMoney",
        translation_key="session_cost",
        icon="mdi:currency-usd",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="RSSI",
        translation_key="wifi_signal",
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: GrizzleConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Grizzl-E sensors."""
    coordinator = entry.runtime_data

    entities: list[SensorEntity] = []
    for description in SENSOR_DESCRIPTIONS:
        entities.append(GrizzleSensor(coordinator, description))

    # Add the text-based state sensors
    entities.append(GrizzleStateSensor(coordinator))
    entities.append(GrizzleErrorSensor(coordinator))
    entities.append(GrizzlePilotSensor(coordinator))

    async_add_entities(entities)


class GrizzleSensor(GrizzleEntity, SensorEntity):
    """Representation of a Grizzl-E sensor."""

    def __init__(
        self,
        coordinator: GrizzleCoordinator,
        description: SensorEntityDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{self._serial}_{description.key}"

    @property
    def native_value(self) -> float | None:
        return self.coordinator.data.get(self.entity_description.key)


class GrizzleStateSensor(GrizzleEntity, SensorEntity):
    """Charger state sensor."""

    _attr_translation_key = "charger_state"
    _attr_icon = "mdi:ev-station"

    def __init__(self, coordinator: GrizzleCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{self._serial}_state"

    @property
    def native_value(self) -> str | None:
        state = self.coordinator.data.get("state")
        if state is not None:
            return CHARGER_STATES.get(state, f"Unknown ({state})")
        return None


class GrizzleErrorSensor(GrizzleEntity, SensorEntity):
    """Charger error sensor."""

    _attr_translation_key = "charger_error"
    _attr_icon = "mdi:alert-circle-outline"
    _attr_entity_registry_enabled_default = False

    def __init__(self, coordinator: GrizzleCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{self._serial}_error"

    @property
    def native_value(self) -> str | None:
        sub_state = self.coordinator.data.get("subState")
        if sub_state is not None:
            return CHARGER_ERRORS.get(sub_state, f"Unknown ({sub_state})")
        return None


class GrizzlePilotSensor(GrizzleEntity, SensorEntity):
    """Pilot (plug) connection sensor."""

    _attr_translation_key = "pilot_state"
    _attr_icon = "mdi:ev-plug-type1"

    def __init__(self, coordinator: GrizzleCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{self._serial}_pilot"

    @property
    def native_value(self) -> str | None:
        pilot = self.coordinator.data.get("pilot")
        if pilot is not None:
            return PILOT_STATES.get(pilot, f"Unknown ({pilot})")
        return None
