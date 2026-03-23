"""Data update coordinator for Grizzl-E."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import GrizzleApi, GrizzleApiError

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=5)


class GrizzleCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator to poll the Grizzl-E charger."""

    def __init__(self, hass: HomeAssistant, api: GrizzleApi) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="Grizzl-E",
            update_interval=SCAN_INTERVAL,
        )
        self.api = api

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from the charger."""
        try:
            return await self.api.get_main_data()
        except GrizzleApiError as err:
            raise UpdateFailed(f"Error fetching data: {err}") from err
