"""API client for Grizzl-E EV Charger."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp

from .const import ENDPOINT_INIT, ENDPOINT_MAIN, ENDPOINT_OCPP_EVENT, ENDPOINT_PAGE_EVENT

_LOGGER = logging.getLogger(__name__)

TIMEOUT = aiohttp.ClientTimeout(total=10)


class GrizzleApiError(Exception):
    """Base exception for Grizzl-E API errors."""


class GrizzleConnectionError(GrizzleApiError):
    """Error connecting to charger."""


class GrizzleApi:
    """API client for communicating with a Grizzl-E charger over the local network."""

    def __init__(self, host: str, session: aiohttp.ClientSession) -> None:
        self._host = host
        self._session = session
        self._base_url = f"http://{host}"

    async def _post(self, endpoint: str, data: str | None = None) -> dict[str, Any]:
        """Send a POST request to the charger."""
        url = f"{self._base_url}{endpoint}"
        headers = {"Content-type": "application/x-www-form-urlencoded"}
        try:
            async with self._session.post(
                url, data=data, headers=headers, timeout=TIMEOUT
            ) as resp:
                resp.raise_for_status()
                return await resp.json(content_type=None)
        except asyncio.TimeoutError as err:
            raise GrizzleConnectionError(
                f"Timeout connecting to charger at {self._host}"
            ) from err
        except aiohttp.ClientError as err:
            raise GrizzleConnectionError(
                f"Error communicating with charger at {self._host}: {err}"
            ) from err

    async def get_init_data(self) -> dict[str, Any]:
        """Get initial configuration data from the charger."""
        return await self._post(ENDPOINT_INIT)

    async def get_main_data(self) -> dict[str, Any]:
        """Get live status data from the charger."""
        return await self._post(ENDPOINT_MAIN)

    async def send_command(self, name: str, value: Any = "") -> None:
        """Send a command to the charger via /pageEvent."""
        url = f"{self._base_url}{ENDPOINT_PAGE_EVENT}"
        headers = {
            "Content-type": "application/x-www-form-urlencoded",
            "pageEvent": name,
        }
        data = f"{name}={value}"
        try:
            async with self._session.post(
                url, data=data, headers=headers, timeout=TIMEOUT
            ) as resp:
                resp.raise_for_status()
        except asyncio.TimeoutError as err:
            raise GrizzleConnectionError(
                f"Timeout sending command to charger at {self._host}"
            ) from err
        except aiohttp.ClientError as err:
            raise GrizzleConnectionError(
                f"Error sending command to charger at {self._host}: {err}"
            ) from err

    async def send_ocpp_command(self, name: str, value: Any = "") -> None:
        """Send a command to the charger via /ocppEvent."""
        url = f"{self._base_url}{ENDPOINT_OCPP_EVENT}"
        headers = {
            "Content-type": "application/x-www-form-urlencoded",
            "pageEvent": name,
        }
        data = f"{name}={value}"
        try:
            async with self._session.post(
                url, data=data, headers=headers, timeout=TIMEOUT
            ) as resp:
                resp.raise_for_status()
        except asyncio.TimeoutError as err:
            raise GrizzleConnectionError(
                f"Timeout sending OCPP command to charger at {self._host}"
            ) from err
        except aiohttp.ClientError as err:
            raise GrizzleConnectionError(
                f"Error sending OCPP command to charger at {self._host}: {err}"
            ) from err

    async def async_validate_connection(self) -> dict[str, Any]:
        """Validate that we can connect to the charger. Returns main data on success."""
        return await self.get_main_data()
