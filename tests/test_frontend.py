"""Tests for the bundled Lovelace card."""

from __future__ import annotations

from http import HTTPStatus
import json
from pathlib import Path
from unittest.mock import patch

from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.test_util.aiohttp import (
    AiohttpClientMocker,
)
from pytest_homeassistant_custom_component.typing import ClientSessionGenerator

from homeassistant.core import HomeAssistant

from .conftest import mock_lidarr

COMPONENT = Path(__file__).parents[1] / "custom_components" / "lidarr_recently_added"
CARD_URL = "/lidarr_recently_added/lidarr-recently-added-card.js"


async def _setup(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
    entry: MockConfigEntry,
) -> None:
    mock_lidarr(aioclient_mock)
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()


async def test_card_is_served(
    hass: HomeAssistant,
    hass_client_no_auth: ClientSessionGenerator,
    aioclient_mock: AiohttpClientMocker,
    mock_config_entry: MockConfigEntry,
) -> None:
    """The bundled card is served, matching the integration's version."""
    await _setup(hass, aioclient_mock, mock_config_entry)
    client = await hass_client_no_auth()
    response = await client.get(CARD_URL)
    assert response.status == HTTPStatus.OK
    body = await response.text()

    version = json.loads((COMPONENT / "manifest.json").read_text())["version"]
    # The bundle is committed; a stale build would carry an older version.
    assert body.startswith(f"/* Lidarr Recently Added card {version} ")
    assert "lidarr-recently-added-card" in body
    # Lit is bundled; nothing is fetched from a CDN at runtime.
    assert "https://cdn" not in body
    assert "unpkg.com" not in body


async def test_card_registered_with_frontend(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
    mock_config_entry: MockConfigEntry,
) -> None:
    """The card loads on every dashboard, with a cache-busting hash."""
    hass.config.components.add("frontend")
    with patch(
        "homeassistant.components.frontend.add_extra_js_url"
    ) as add_extra_js_url:
        await _setup(hass, aioclient_mock, mock_config_entry)

    add_extra_js_url.assert_called_once()
    url = add_extra_js_url.call_args.args[1]
    path, _, query = url.partition("?")
    assert path == CARD_URL
    assert query.startswith("v=")
    assert len(query) == len("v=") + 12


async def test_card_not_registered_without_frontend(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Without the frontend there is nothing to register with."""
    with patch(
        "homeassistant.components.frontend.add_extra_js_url"
    ) as add_extra_js_url:
        await _setup(hass, aioclient_mock, mock_config_entry)
    add_extra_js_url.assert_not_called()
