"""Diagnostics support for Lidarr Recently Added."""

from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.const import CONF_API_KEY, CONF_URL
from homeassistant.core import HomeAssistant

from .const import CONF_LINK_URL
from .coordinator import ImageRef, LidarrRecentlyAddedConfigEntry

TO_REDACT = {
    CONF_API_KEY,
    CONF_URL,
    CONF_LINK_URL,
    "lidarr_url",
    "appData",
    "startupPath",
    "urlBase",
    "instanceName",
}


def _describe_image(image: ImageRef | None) -> str | None:
    """Describe which cached image an item uses, without a signed URL."""
    return f"{image.kind}/{image.item_id}/{image.filename}" if image else None


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
                "max_albums": coordinator.max_albums,
                "max_artists": coordinator.max_artists,
                "separate_link_url": coordinator.link_base_url
                != coordinator.client.base_url,
            },
            "albums": (
                [item.as_dict(_describe_image) for item in data.albums]
                if data and data.albums is not None
                else None
            ),
            "artists": (
                [item.as_dict(_describe_image) for item in data.artists]
                if data and data.artists is not None
                else None
            ),
        },
        TO_REDACT,
    )
