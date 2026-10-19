"""Config flow for Lidarr Recently Added."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlowWithReload,
)
from homeassistant.const import CONF_API_KEY, CONF_URL, CONF_VERIFY_SSL
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import SectionConfig, section
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .api import (
    InvalidUrlError,
    LidarrAuthenticationError,
    LidarrClient,
    LidarrError,
    normalize_url,
)
from .const import (
    CONF_ADVANCED,
    CONF_ALBUMS_ENABLED,
    CONF_ARTISTS_ENABLED,
    CONF_LINK_URL,
    CONF_MAX_ALBUMS,
    CONF_MAX_ARTISTS,
    CONF_MAX_ITEMS,
    CONF_SCAN_INTERVAL,
    DEFAULT_MAX_ITEMS,
    DEFAULT_NAME,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_VERIFY_SSL,
    DOMAIN,
    LOGGER,
    MAX_MAX_ITEMS,
    MAX_SCAN_INTERVAL,
    MIN_MAX_ITEMS,
    MIN_SCAN_INTERVAL,
)


class NotLidarrError(Exception):
    """The server answered, but it isn't Lidarr."""


async def _async_validate(
    hass: HomeAssistant, url: str, api_key: str, verify_ssl: bool
) -> dict[str, Any]:
    """Connect to Lidarr and return its system status."""
    client = LidarrClient(
        async_get_clientsession(hass, verify_ssl=verify_ssl), url, api_key
    )
    status = await client.async_get_system_status()
    # Readarr and Prowlarr also serve /api/v1/system/status.
    if str(status.get("appName", "")).lower() != "lidarr":
        raise NotLidarrError
    return status


async def _async_errors_for(
    hass: HomeAssistant, url: str, api_key: str, verify_ssl: bool
) -> tuple[dict[str, str], dict[str, Any] | None]:
    """Validate and map failures to form errors."""
    try:
        status = await _async_validate(hass, url, api_key, verify_ssl)
    except LidarrAuthenticationError:
        return {"base": "invalid_auth"}, None
    except LidarrError:
        return {"base": "cannot_connect"}, None
    except NotLidarrError:
        return {"base": "not_lidarr"}, None
    except Exception:  # noqa: BLE001
        LOGGER.exception("Unexpected error validating Lidarr connection")
        return {"base": "unknown"}, None
    return {}, status


class LidarrRecentlyAddedConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Lidarr Recently Added."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> LidarrRecentlyAddedOptionsFlow:
        """Return the options flow."""
        return LidarrRecentlyAddedOptionsFlow()

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                url = normalize_url(user_input[CONF_URL])
            except InvalidUrlError:
                errors[CONF_URL] = "invalid_url"
            else:
                await self.async_set_unique_id(url)
                self._abort_if_unique_id_configured()
                errors, status = await _async_errors_for(
                    self.hass,
                    url,
                    user_input[CONF_API_KEY],
                    user_input[CONF_VERIFY_SSL],
                )
                if status is not None:
                    return self.async_create_entry(
                        title=status.get("instanceName") or DEFAULT_NAME,
                        data={**user_input, CONF_URL: url},
                    )

        return self.async_show_form(
            step_id="user",
            data_schema=self.add_suggested_values_to_schema(
                vol.Schema(
                    {
                        vol.Required(CONF_URL): TextSelector(
                            TextSelectorConfig(type=TextSelectorType.URL)
                        ),
                        vol.Required(CONF_API_KEY): TextSelector(
                            TextSelectorConfig(type=TextSelectorType.PASSWORD)
                        ),
                        vol.Required(CONF_VERIFY_SSL, default=DEFAULT_VERIFY_SSL): bool,
                    }
                ),
                {k: v for k, v in (user_input or {}).items() if k != CONF_API_KEY},
            ),
            description_placeholders={
                "example_url": "http://192.168.1.10:8686",
                "example_proxy_url": "https://example.com/lidarr",
            },
            errors=errors,
        )

    async def async_step_reauth(
        self, entry_data: Mapping[str, Any]
    ) -> ConfigFlowResult:
        """Start reauthentication after Lidarr rejected the API key."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Ask for a new API key."""
        entry = self._get_reauth_entry()
        errors: dict[str, str] = {}
        if user_input is not None:
            errors, status = await _async_errors_for(
                self.hass,
                entry.data[CONF_URL],
                user_input[CONF_API_KEY],
                entry.data.get(CONF_VERIFY_SSL, DEFAULT_VERIFY_SSL),
            )
            if status is not None:
                return self.async_update_reload_and_abort(
                    entry, data_updates={CONF_API_KEY: user_input[CONF_API_KEY]}
                )

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_API_KEY): TextSelector(
                        TextSelectorConfig(type=TextSelectorType.PASSWORD)
                    )
                }
            ),
            description_placeholders={"url": entry.data[CONF_URL]},
            errors=errors,
        )


class LidarrRecentlyAddedOptionsFlow(OptionsFlowWithReload):
    """Options: item count, poll interval and which sensors to create."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the options."""
        errors: dict[str, str] = {}
        if user_input is not None:
            advanced = user_input.pop(CONF_ADVANCED, {})
            options: dict[str, Any] = {
                **user_input,
                CONF_MAX_ALBUMS: int(user_input[CONF_MAX_ALBUMS]),
                CONF_MAX_ARTISTS: int(user_input[CONF_MAX_ARTISTS]),
                CONF_SCAN_INTERVAL: int(user_input[CONF_SCAN_INTERVAL]),
            }
            if link_url := (advanced.get(CONF_LINK_URL) or "").strip():
                # Only checked for shape: Home Assistant may not be able to
                # reach the address people browse to.
                try:
                    options[CONF_LINK_URL] = normalize_url(link_url)
                except InvalidUrlError:
                    errors["base"] = "invalid_link_url"
            if not errors:
                return self.async_create_entry(data=options)

        count_selector = NumberSelectorConfig(
            min=MIN_MAX_ITEMS, max=MAX_MAX_ITEMS, step=1, mode=NumberSelectorMode.BOX
        )
        schema = vol.Schema(
            {
                vol.Required(
                    CONF_MAX_ALBUMS, default=DEFAULT_MAX_ITEMS
                ): NumberSelector(count_selector),
                vol.Required(
                    CONF_MAX_ARTISTS, default=DEFAULT_MAX_ITEMS
                ): NumberSelector(count_selector),
                vol.Required(
                    CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
                ): NumberSelector(
                    NumberSelectorConfig(
                        min=MIN_SCAN_INTERVAL,
                        max=MAX_SCAN_INTERVAL,
                        step=1,
                        mode=NumberSelectorMode.BOX,
                        unit_of_measurement="min",
                    )
                ),
                vol.Required(CONF_ALBUMS_ENABLED, default=True): bool,
                vol.Required(CONF_ARTISTS_ENABLED, default=True): bool,
                vol.Required(CONF_ADVANCED): section(
                    vol.Schema(
                        {
                            vol.Optional(CONF_LINK_URL): TextSelector(
                                TextSelectorConfig(type=TextSelectorType.URL)
                            ),
                        }
                    ),
                    SectionConfig(collapsed=True),
                ),
            }
        )
        current = user_input or dict(self.config_entry.options)
        # Options saved before 0.3.0 had one count for both lists.
        if CONF_MAX_ITEMS in current:
            legacy = current.pop(CONF_MAX_ITEMS)
            current.setdefault(CONF_MAX_ALBUMS, legacy)
            current.setdefault(CONF_MAX_ARTISTS, legacy)
        suggested = {
            **current,
            CONF_ADVANCED: {
                CONF_LINK_URL: (
                    advanced.get(CONF_LINK_URL)
                    if user_input is not None
                    else current.get(CONF_LINK_URL)
                )
                or ""
            },
        }
        return self.async_show_form(
            step_id="init",
            data_schema=self.add_suggested_values_to_schema(schema, suggested),
            errors=errors,
        )
