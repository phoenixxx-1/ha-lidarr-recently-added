"""The Lidarr Recently Added integration."""

from __future__ import annotations

import hashlib
from pathlib import Path

from homeassistant.components.http import StaticPathConfig
from homeassistant.const import CONF_API_KEY, CONF_URL, CONF_VERIFY_SSL, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.typing import ConfigType

from .api import LidarrAuthenticationError, LidarrClient, LidarrError
from .const import (
    CARD_FILENAME,
    CARD_URL_BASE,
    DEFAULT_VERIFY_SSL,
    DOMAIN,
    LOGGER,
)
from .coordinator import (
    LidarrRecentlyAddedConfigEntry,
    LidarrRecentlyAddedCoordinator,
    LidarrRecentlyAddedRuntimeData,
)
from .views import LidarrImageView

PLATFORMS: list[Platform] = [Platform.SENSOR]

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


CARD_PATH = Path(__file__).parent / "frontend" / CARD_FILENAME


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Register the image proxy and the bundled card, once for all entries."""
    hass.http.register_view(LidarrImageView())
    await _async_register_card(hass)
    return True


async def _async_register_card(hass: HomeAssistant) -> None:
    """Serve the bundled Lovelace card and load it on every dashboard.

    The card ships inside the integration so it always matches the sensors'
    attributes. It is loaded with ``add_extra_js_url`` (which works for
    storage and YAML dashboards alike) rather than by editing the user's
    Lovelace resources. A content hash in the URL makes browsers fetch the
    new file after an update.
    """
    url = f"{CARD_URL_BASE}/{CARD_FILENAME}"
    digest = await hass.async_add_executor_job(_file_digest, CARD_PATH)
    await hass.http.async_register_static_paths(
        [StaticPathConfig(url, str(CARD_PATH), cache_headers=True)]
    )
    if "frontend" in hass.config.components:
        # Imported here: frontend is only an after-dependency.
        from homeassistant.components.frontend import add_extra_js_url  # noqa: PLC0415

        add_extra_js_url(hass, f"{url}?v={digest}")
    else:
        LOGGER.debug("Frontend not loaded; the card is served at %s", url)


def _file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:12]


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
