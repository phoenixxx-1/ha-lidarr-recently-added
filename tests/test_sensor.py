"""Tests for the sensors."""

from __future__ import annotations

import json

from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.lidarr_recently_added.const import DOMAIN
from custom_components.lidarr_recently_added.sensor import LidarrRecentlyAddedSensor
from homeassistant.const import ATTR_DEVICE_CLASS
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr, entity_registry as er

from .conftest import API_KEY, URL

ALBUM_KEYS = {
    "artist",
    "album",
    "release_date",
    "added",
    "cover_url",
    "album_type",
    "track_count",
    "musicbrainz_id",
    "lidarr_url",
}
ARTIST_KEYS = {
    "artist",
    "added",
    "image_url",
    "album_count",
    "musicbrainz_id",
    "lidarr_url",
}


async def test_album_sensor(
    hass: HomeAssistant, setup_integration: MockConfigEntry
) -> None:
    """The album sensor's state is the newest import; items are grouped."""
    state = hass.states.get("sensor.lidarr_recently_added_albums")
    assert state.state == "2026-10-18T20:00:03+00:00"
    assert state.attributes[ATTR_DEVICE_CLASS] == "timestamp"

    items = state.attributes["items"]
    assert [item["album"] for item in items] == ["Album 1", "Album 2", "Album 3"]
    assert [item["artist"] for item in items] == ["Alpha", "Bravo", "Charlie"]
    assert all(set(item) == ALBUM_KEYS for item in items)
    assert items[0]["track_count"] == 11
    assert items[0]["lidarr_url"] == f"{URL}/album/mb-album-1"


async def test_artist_sensor(
    hass: HomeAssistant, setup_integration: MockConfigEntry
) -> None:
    """The artist sensor is sorted by added date and skips undated artists."""
    state = hass.states.get("sensor.lidarr_recently_added_artists")
    assert state.state == "2026-10-18T12:00:00+00:00"

    items = state.attributes["items"]
    assert [item["artist"] for item in items] == [
        "Newest",
        "Artist 4",
        "Artist 3",
        "Artist 1",
    ]
    assert all(set(item) == ARTIST_KEYS for item in items)


async def test_no_secrets_or_local_paths_in_states(
    hass: HomeAssistant, setup_integration: MockConfigEntry
) -> None:
    """No API key or authenticated MediaCover path appears in any state."""
    dumped = json.dumps(
        [state.as_dict() for state in hass.states.async_all()], default=str
    )
    assert API_KEY not in dumped
    assert "apikey" not in dumped.lower()
    assert "/MediaCover" not in dumped
    assert "/api/v1" not in dumped


async def test_items_not_recorded() -> None:
    """The items list is excluded from the recorder."""
    assert "items" in LidarrRecentlyAddedSensor._unrecorded_attributes


async def test_empty_library(
    hass: HomeAssistant,
    aioclient_mock,
    mock_config_entry: MockConfigEntry,
) -> None:
    """With nothing imported the state is unknown and items is empty."""
    from .conftest import mock_lidarr

    mock_lidarr(aioclient_mock, history=[], artists=[])
    mock_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    state = hass.states.get("sensor.lidarr_recently_added_albums")
    assert state.state == "unknown"
    assert state.attributes["items"] == []


async def test_device(
    hass: HomeAssistant,
    setup_integration: MockConfigEntry,
    device_registry: dr.DeviceRegistry,
    entity_registry: er.EntityRegistry,
) -> None:
    """Both sensors belong to one service device linking to Lidarr."""
    device = device_registry.async_get_device_by_identifier(
        (DOMAIN, setup_integration.entry_id), setup_integration.entry_id
    )
    assert device is not None
    assert device.entry_type is dr.DeviceEntryType.SERVICE
    assert device.configuration_url == URL
    assert device.sw_version == "3.1.2.4913"
    assert device.manufacturer == "Lidarr"

    entities = er.async_entries_for_device(entity_registry, device.id)
    assert {entity.unique_id for entity in entities} == {
        f"{setup_integration.entry_id}_recently_added_albums",
        f"{setup_integration.entry_id}_recently_added_artists",
    }
