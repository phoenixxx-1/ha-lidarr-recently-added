"""Tests for setup, unload, availability and recovery."""

from __future__ import annotations

import aiohttp
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.test_util.aiohttp import (
    AiohttpClientMocker,
)

from custom_components.lidarr_recently_added.const import DOMAIN
from homeassistant.config_entries import SOURCE_REAUTH, ConfigEntryState
from homeassistant.const import STATE_UNAVAILABLE
from homeassistant.core import HomeAssistant

from .conftest import URL, mock_lidarr

ALBUMS = "sensor.lidarr_recently_added_albums"
ARTISTS = "sensor.lidarr_recently_added_artists"


async def test_setup_and_unload(
    hass: HomeAssistant, setup_integration: MockConfigEntry
) -> None:
    """The entry loads and unloads cleanly."""
    assert setup_integration.state is ConfigEntryState.LOADED
    assert await hass.config_entries.async_unload(setup_integration.entry_id)
    await hass.async_block_till_done()
    assert setup_integration.state is ConfigEntryState.NOT_LOADED


async def test_setup_retry_when_unreachable(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
    mock_config_entry: MockConfigEntry,
) -> None:
    """An unreachable Lidarr makes setup retry later."""
    aioclient_mock.get(
        f"{URL}/api/v1/system/status", exc=aiohttp.ClientConnectionError()
    )
    mock_config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    assert mock_config_entry.state is ConfigEntryState.SETUP_RETRY


async def test_setup_auth_failure_starts_reauth(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
    mock_config_entry: MockConfigEntry,
) -> None:
    """A 401 at setup starts the reauth flow."""
    aioclient_mock.get(f"{URL}/api/v1/system/status", status=401)
    mock_config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert mock_config_entry.state is ConfigEntryState.SETUP_ERROR
    flows = hass.config_entries.flow.async_progress_by_handler(DOMAIN)
    assert len(flows) == 1
    assert flows[0]["context"]["source"] == SOURCE_REAUTH


async def test_unavailable_then_recovers(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
    setup_integration: MockConfigEntry,
) -> None:
    """A failed refresh makes the sensors unavailable until Lidarr is back."""
    coordinator = setup_integration.runtime_data.coordinator
    assert hass.states.get(ALBUMS).state != STATE_UNAVAILABLE

    aioclient_mock.clear_requests()
    aioclient_mock.get(f"{URL}/api/v1/history", exc=aiohttp.ClientConnectionError())
    aioclient_mock.get(f"{URL}/api/v1/artist", exc=aiohttp.ClientConnectionError())
    await coordinator.async_refresh()
    await hass.async_block_till_done()
    assert hass.states.get(ALBUMS).state == STATE_UNAVAILABLE
    assert hass.states.get(ARTISTS).state == STATE_UNAVAILABLE

    aioclient_mock.clear_requests()
    mock_lidarr(aioclient_mock)
    await coordinator.async_refresh()
    await hass.async_block_till_done()
    assert hass.states.get(ALBUMS).state == "2026-10-18T20:00:03+00:00"
    assert hass.states.get(ARTISTS).state == "2026-10-18T12:00:00+00:00"


async def test_refresh_auth_failure_starts_reauth(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
    setup_integration: MockConfigEntry,
) -> None:
    """A 401 during a refresh starts reauth and marks the sensors unavailable."""
    aioclient_mock.clear_requests()
    aioclient_mock.get(f"{URL}/api/v1/history", status=401)
    await setup_integration.runtime_data.coordinator.async_refresh()
    await hass.async_block_till_done()

    assert hass.states.get(ALBUMS).state == STATE_UNAVAILABLE
    flows = hass.config_entries.flow.async_progress_by_handler(DOMAIN)
    assert [flow["context"]["source"] for flow in flows] == [SOURCE_REAUTH]
