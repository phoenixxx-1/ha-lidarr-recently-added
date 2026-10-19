"""The Lidarr Recently Added integration."""

from __future__ import annotations

from homeassistant.const import CONF_API_KEY, CONF_URL, CONF_VERIFY_SSL, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.typing import ConfigType

from .api import LidarrAuthenticationError, LidarrClient, LidarrError
from .const import DEFAULT_VERIFY_SSL, DOMAIN
from .coordinator import (
    LidarrRecentlyAddedConfigEntry,
    LidarrRecentlyAddedCoordinator,
    LidarrRecentlyAddedRuntimeData,
)
from .views import LidarrImageView

PLATFORMS: list[Platform] = [Platform.SENSOR]

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Register the image proxy once, for every config entry."""
    hass.http.register_view(LidarrImageView())
    return True


async def async_setup_entry(
    hass: HomeAssistant, entry: LidarrRecentlyAddedConfigEntry
) -> bool:
    """Set up Lidarr Recently Added from a config entry."""
    client = LidarrClient(
        async_get_clientsession(
            hass, verify_ssl=entry.data.get(CONF_VERIFY_SSL, DEFAULT_VERIFY_SSL)
        ),
        entry.data[CONF_URL],
        entry.data[CONF_API_KEY],
    )
    try:
        system_status = await client.async_get_system_status()
    except LidarrAuthenticationError as err:
        raise ConfigEntryAuthFailed(str(err)) from err
    except LidarrError as err:
        raise ConfigEntryNotReady(str(err)) from err

    coordinator = LidarrRecentlyAddedCoordinator(hass, entry, client)
    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = LidarrRecentlyAddedRuntimeData(
        coordinator=coordinator, system_status=system_status
    )
    entry.async_on_unload(coordinator.async_start_event_listener())

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: LidarrRecentlyAddedConfigEntry
) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
