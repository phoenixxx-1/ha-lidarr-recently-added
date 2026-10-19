"""Tests for the config, reauth and options flows."""

from __future__ import annotations

from unittest.mock import patch

import aiohttp
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.test_util.aiohttp import (
    AiohttpClientMocker,
)

from custom_components.lidarr_recently_added.const import (
    CONF_ALBUMS_ENABLED,
    CONF_ARTISTS_ENABLED,
    CONF_MAX_ITEMS,
    CONF_SCAN_INTERVAL,
    DOMAIN,
)
from homeassistant.config_entries import SOURCE_USER
from homeassistant.const import CONF_API_KEY, CONF_URL, CONF_VERIFY_SSL
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers import entity_registry as er

from .conftest import API_KEY, SYSTEM_STATUS, URL, mock_lidarr

USER_INPUT = {CONF_URL: URL, CONF_API_KEY: API_KEY, CONF_VERIFY_SSL: True}


async def test_user_flow_success(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    """A valid URL and key create an entry with a normalised URL."""
    aioclient_mock.get(
        f"{URL}/api/v1/system/status",
        json={**SYSTEM_STATUS, "instanceName": "Music"},
    )
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"
    assert set(result["description_placeholders"]) == {
        "example_url",
        "example_proxy_url",
    }

    with patch(
        "custom_components.lidarr_recently_added.async_setup_entry", return_value=True
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {**USER_INPUT, CONF_URL: " HTTP://Lidarr.Local:8686/ "},
        )
        await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Music"
    assert result["data"] == USER_INPUT
    assert result["result"].unique_id == URL

    # The key is sent as a header, never in the URL.
    _, url, _, headers = aioclient_mock.mock_calls[-1]
    assert headers["X-Api-Key"] == API_KEY
    assert API_KEY not in str(url)


async def test_user_flow_keeps_base_path(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
) -> None:
    """A reverse-proxy base path is kept and used for API calls."""
    aioclient_mock.get(
        "https://example.com/lidarr/api/v1/system/status", json=SYSTEM_STATUS
    )
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    with patch(
        "custom_components.lidarr_recently_added.async_setup_entry", return_value=True
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {**USER_INPUT, CONF_URL: "https://example.com:443/lidarr/"},
        )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"][CONF_URL] == "https://example.com/lidarr"
    assert result["title"] == "Lidarr"


@pytest.mark.parametrize(
    ("mock_kwargs", "error"),
    [
        ({"status": 401}, "invalid_auth"),
        ({"status": 403}, "invalid_auth"),
        ({"exc": aiohttp.ClientConnectionError()}, "cannot_connect"),
        ({"exc": TimeoutError()}, "cannot_connect"),
        ({"status": 500}, "cannot_connect"),
        ({"status": 302}, "cannot_connect"),
        ({"text": "<html>login</html>"}, "cannot_connect"),
        ({"json": {**SYSTEM_STATUS, "appName": "Readarr"}}, "not_lidarr"),
    ],
)
async def test_user_flow_errors(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
    mock_kwargs: dict,
    error: str,
) -> None:
    """Each failure maps to its own error, and the user can recover."""
    aioclient_mock.get(f"{URL}/api/v1/system/status", **mock_kwargs)
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], USER_INPUT
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": error}

    aioclient_mock.clear_requests()
    aioclient_mock.get(f"{URL}/api/v1/system/status", json=SYSTEM_STATUS)
    with patch(
        "custom_components.lidarr_recently_added.async_setup_entry", return_value=True
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], USER_INPUT
        )
    assert result["type"] is FlowResultType.CREATE_ENTRY


async def test_user_flow_unknown_error(hass: HomeAssistant) -> None:
    """An unexpected exception shows the unknown error."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    with patch(
        "custom_components.lidarr_recently_added.config_flow.LidarrClient.async_get_system_status",
        side_effect=RuntimeError("boom"),
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], USER_INPUT
        )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "unknown"}


@pytest.mark.parametrize("url", ["lidarr.local:8686", "ftp://lidarr.local", "http://"])
async def test_user_flow_invalid_url(hass: HomeAssistant, url: str) -> None:
    """A URL without an http(s) scheme and host is rejected on the field."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {**USER_INPUT, CONF_URL: url}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {CONF_URL: "invalid_url"}


async def test_user_flow_already_configured(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry
) -> None:
    """The same instance, written differently, can't be added twice."""
    mock_config_entry.add_to_hass(hass)
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {**USER_INPUT, CONF_URL: "http://LIDARR.local:8686/"}
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_reauth(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Reauth rejects a bad key, then stores a good one."""
    mock_config_entry.add_to_hass(hass)
    result = await mock_config_entry.start_reauth_flow(hass)
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "reauth_confirm"

    aioclient_mock.get(f"{URL}/api/v1/system/status", status=401)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_API_KEY: "wrong"}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "invalid_auth"}

    aioclient_mock.clear_requests()
    aioclient_mock.get(f"{URL}/api/v1/system/status", json=SYSTEM_STATUS)
    with patch(
        "custom_components.lidarr_recently_added.async_setup_entry", return_value=True
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"], {CONF_API_KEY: "new-key"}
        )
        await hass.async_block_till_done()
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reauth_successful"
    assert mock_config_entry.data[CONF_API_KEY] == "new-key"
    assert mock_config_entry.data[CONF_URL] == URL


async def test_options_flow(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
    setup_integration: MockConfigEntry,
    entity_registry: er.EntityRegistry,
) -> None:
    """Options are stored, the entry reloads, and a disabled sensor is removed."""
    entry = setup_integration
    assert hass.states.get("sensor.lidarr_recently_added_albums") is not None

    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "init"

    aioclient_mock.clear_requests()
    mock_lidarr(aioclient_mock)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {
            CONF_MAX_ITEMS: 2.0,
            CONF_SCAN_INTERVAL: 60.0,
            CONF_ALBUMS_ENABLED: False,
            CONF_ARTISTS_ENABLED: True,
        },
    )
    await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert entry.options == {
        CONF_MAX_ITEMS: 2,
        CONF_SCAN_INTERVAL: 60,
        CONF_ALBUMS_ENABLED: False,
        CONF_ARTISTS_ENABLED: True,
    }
    coordinator = entry.runtime_data.coordinator
    assert coordinator.max_items == 2
    assert coordinator.update_interval.total_seconds() == 3600
    assert coordinator.data.albums is None

    assert hass.states.get("sensor.lidarr_recently_added_albums") is None
    assert entity_registry.async_get("sensor.lidarr_recently_added_albums") is None
    artists = hass.states.get("sensor.lidarr_recently_added_artists")
    assert len(artists.attributes["items"]) == 2
    # Albums are off, so history isn't requested at all.
    assert not any("/history" in str(call[1]) for call in aioclient_mock.mock_calls)
