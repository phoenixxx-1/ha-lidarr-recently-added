"""Diagnostics support for Lidarr Recently Added."""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.const import CONF_API_KEY, CONF_URL
from homeassistant.core import HomeAssistant

from .coordinator import LidarrRecentlyAddedConfigEntry

TO_REDACT = {
    CONF_API_KEY,
    CONF_URL,
    "lidarr_url",
    "appData",
    "startupPath",
    "urlBase",
    "instanceName",
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: LidarrRecentlyAddedConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    runtime = entry.runtime_data
    coordinator = runtime.coordinator
    data = coordinator.data
    return async_redact_data(
        {
            "entry": {
                "data": dict(entry.data),
                "options": dict(entry.options),
            },
            "system_status": {
                key: runtime.system_status.get(key)
                for key in (
                    "appName",
                    "version",
                    "branch",
                    "osName",
                    "isDocker",
                    "urlBase",
                    "instanceName",
                )
            },
            "coordinator": {
                "last_update_success": coordinator.last_update_success,
                "update_interval": str(coordinator.update_interval),
                "max_items": coordinator.max_items,
            },
            "albums": (
                [item.as_dict() for item in data.albums]
                if data and data.albums is not None
                else None
            ),
            "artists": (
                [item.as_dict() for item in data.artists]
                if data and data.artists is not None
                else None
            ),
        },
        TO_REDACT,
    )
