"""Tests for the sensors."""

from __future__ import annotations

from datetime import UTC, datetime
import json

from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.test_util.aiohttp import (
    AiohttpClientMocker,
)

from custom_components.lidarr_recently_added.const import DOMAIN
from custom_components.lidarr_recently_added.coordinator import ArtistItem
from custom_components.lidarr_recently_added.sensor import (
    LidarrRecentlyAddedSensor,
    _latest_title,
)
from homeassistant.const import ATTR_DEVICE_CLASS
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr, entity_registry as er

from .conftest import (
    API_KEY,
    SYSTEM_STATUS,
    URL,
    album_details,
    assert_signed_image,
    history_record,
    mock_lidarr,
)

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
    for item, album_id in zip(items, (1, 2, 3), strict=True):
        assert_signed_image(
            item["cover_url"],
            setup_integration.entry_id,
            "album",
            album_id,
            "cover-500.jpg",
            "42",
        )


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
        "Artist 6",
    ]
    assert all(set(item) == ARTIST_KEYS for item in items)
    # Artist 4's remoteUrl values are paths inside Lidarr: still an image.
    assert_signed_image(
        items[1]["image_url"],
        setup_integration.entry_id,
        "artist",
        4,
        "poster-500.jpg",
        "63",
    )
    # Artist 6 has no images at all.
    assert items[4]["image_url"] is None


async def test_no_secrets_or_lidarr_paths_in_states(
    hass: HomeAssistant, setup_integration: MockConfigEntry
) -> None:
    """No API key, Lidarr path or third-party image URL appears in any state."""
    dumped = json.dumps(
        [state.as_dict() for state in hass.states.async_all()], default=str
    )
    assert API_KEY not in dumped
    assert "apikey" not in dumped.lower()
    assert "/MediaCover" not in dumped
    assert "/api/v1" not in dumped
    assert "/config/" not in dumped
    assert "coverartarchive" not in dumped
    assert "images.lidarr.audio" not in dumped


async def test_image_attributes_not_recorded() -> None:
    """The list and the signed image URLs are excluded from the recorder."""
    assert LidarrRecentlyAddedSensor._unrecorded_attributes >= {
        "items",
        "entity_picture",
        "cover_url",
        "image_url",
    }


async def test_image_urls_stable_between_refreshes(
    hass: HomeAssistant, setup_integration: MockConfigEntry
) -> None:
    """Signed URLs are reused, so a refresh doesn't change the attributes."""
    before = hass.states.get("sensor.lidarr_recently_added_albums").attributes
    await setup_integration.runtime_data.coordinator.async_refresh()
    await hass.async_block_till_done()
    after = hass.states.get("sensor.lidarr_recently_added_albums").attributes
    assert after["entity_picture"] == before["entity_picture"]
    assert after["items"] == before["items"]


async def test_empty_library(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
    mock_config_entry: MockConfigEntry,
) -> None:
    """With nothing imported the state is unknown and items is empty."""
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
    """All sensors belong to one service device linking to Lidarr."""
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
        f"{setup_integration.entry_id}_latest_album",
        f"{setup_integration.entry_id}_latest_artist",
    }


async def test_pictures_on_list_sensors(
    hass: HomeAssistant, setup_integration: MockConfigEntry
) -> None:
    """The list sensors show the newest item's image through the proxy."""
    entry_id = setup_integration.entry_id
    albums = hass.states.get("sensor.lidarr_recently_added_albums")
    assert_signed_image(
        albums.attributes["entity_picture"], entry_id, "album", 1, "cover-500.jpg", "42"
    )
    artists = hass.states.get("sensor.lidarr_recently_added_artists")
    assert_signed_image(
        artists.attributes["entity_picture"],
        entry_id,
        "artist",
        2,
        "poster-500.jpg",
        "63",
    )


async def test_latest_album_sensor(
    hass: HomeAssistant, setup_integration: MockConfigEntry
) -> None:
    """The latest album sensor shows a readable title, cover and the item."""
    state = hass.states.get("sensor.lidarr_latest_album")
    assert state.state == "Alpha – Album 1"
    assert_signed_image(
        state.attributes["entity_picture"],
        setup_integration.entry_id,
        "album",
        1,
        "cover-500.jpg",
        "42",
    )
    assert state.attributes["cover_url"] == state.attributes["entity_picture"]
    assert ATTR_DEVICE_CLASS not in state.attributes
    assert set(state.attributes) >= ALBUM_KEYS
    assert state.attributes["added"] == "2026-10-18T20:00:03+00:00"
    assert "items" not in state.attributes


async def test_latest_artist_sensor(
    hass: HomeAssistant, setup_integration: MockConfigEntry
) -> None:
    """The latest artist sensor shows the artist name and image."""
    state = hass.states.get("sensor.lidarr_latest_artist")
    assert state.state == "Newest"
    assert_signed_image(
        state.attributes["entity_picture"],
        setup_integration.entry_id,
        "artist",
        2,
        "poster-500.jpg",
        "63",
    )
    assert set(state.attributes) >= ARTIST_KEYS


async def test_latest_sensors_without_images_or_items(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
    mock_config_entry: MockConfigEntry,
) -> None:
    """No images means no picture; no items means unknown."""
    record = history_record(1, 7, "2026-10-18T20:00:00Z", artist="Alpha")
    record["album"]["images"] = []
    aioclient_mock.get(f"{URL}/api/v1/system/status", json=SYSTEM_STATUS)
    aioclient_mock.get(
        f"{URL}/api/v1/history?page=1",
        json={"page": 1, "pageSize": 250, "totalRecords": 1, "records": [record]},
    )
    aioclient_mock.get(f"{URL}/api/v1/album", json=[{**album_details(7), "images": []}])
    aioclient_mock.get(f"{URL}/api/v1/artist", json=[])
    mock_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    album = hass.states.get("sensor.lidarr_latest_album")
    assert album.state == "Alpha – Album 7"
    assert "entity_picture" not in album.attributes
    assert album.attributes["cover_url"] is None
    artist = hass.states.get("sensor.lidarr_latest_artist")
    assert artist.state == "unknown"
    assert "entity_picture" not in artist.attributes


def test_latest_title_is_truncated() -> None:
    """Titles longer than a state allows are cut with an ellipsis."""
    item = ArtistItem(
        artist_id=1,
        artist="x" * 400,
        added=datetime(2026, 1, 1, tzinfo=UTC),
        image=None,
        album_count=None,
        musicbrainz_id=None,
        lidarr_url=None,
    )
    title = _latest_title([item])
    assert len(title) == 255
    assert title.endswith("…")
