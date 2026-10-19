"""Tests for new-item events."""

from __future__ import annotations

from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_capture_events,
)
from pytest_homeassistant_custom_component.test_util.aiohttp import (
    AiohttpClientMocker,
)

from custom_components.lidarr_recently_added.const import (
    EVENT_NEW_ALBUM,
    EVENT_NEW_ARTIST,
)
from homeassistant.core import HomeAssistant

from .conftest import (
    API_KEY,
    artist_entry,
    default_artists,
    default_history,
    history_record,
    mock_lidarr,
)


async def _refresh(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    await entry.runtime_data.coordinator.async_refresh()
    await hass.async_block_till_done()


async def test_no_events_on_first_refresh(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Start-up doesn't announce the existing list."""
    album_events = async_capture_events(hass, EVENT_NEW_ALBUM)
    artist_events = async_capture_events(hass, EVENT_NEW_ARTIST)
    mock_lidarr(aioclient_mock)
    mock_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    assert album_events == []
    assert artist_events == []

    # An unchanged refresh doesn't fire either.
    await _refresh(hass, mock_config_entry)
    assert album_events == []
    assert artist_events == []


async def test_events_for_new_items(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
    setup_integration: MockConfigEntry,
) -> None:
    """New albums and artists each fire one event with the item's fields."""
    album_events = async_capture_events(hass, EVENT_NEW_ALBUM)
    artist_events = async_capture_events(hass, EVENT_NEW_ARTIST)

    aioclient_mock.clear_requests()
    mock_lidarr(
        aioclient_mock,
        history=[
            history_record(13, 9, "2026-10-19T09:00:01Z", artist="Delta", track_id=2),
            history_record(12, 9, "2026-10-19T09:00:00Z", artist="Delta", track_id=1),
            history_record(11, 8, "2026-10-19T08:00:00Z", artist="Echo"),
            *default_history(),
        ],
        artists=[*default_artists(), artist_entry(42, "2026-10-19T09:00:00Z")],
    )
    await _refresh(hass, setup_integration)

    # Oldest first, one per album despite per-track records.
    assert [event.data["album"] for event in album_events] == ["Album 8", "Album 9"]
    assert album_events[1].data == {
        "artist": "Delta",
        "album": "Album 9",
        "release_date": "2024-05-17",
        "added": "2026-10-19T09:00:01+00:00",
        "cover_url": "https://coverartarchive.org/release/9/front.jpg",
        "album_type": "Album",
        "track_count": 19,
        "musicbrainz_id": "mb-album-9",
        "lidarr_url": "http://lidarr.local:8686/album/mb-album-9",
        "config_entry_id": setup_integration.entry_id,
    }
    assert [event.data["artist"] for event in artist_events] == ["Artist 42"]
    assert API_KEY not in str([e.data for e in album_events + artist_events])

    # The sensor already shows the new album when the event fires.
    state = hass.states.get("sensor.lidarr_recently_added_albums")
    assert state.attributes["items"][0]["album"] == "Album 9"

    # Nothing new on the next refresh.
    await _refresh(hass, setup_integration)
    assert len(album_events) == 2
    assert len(artist_events) == 1


async def test_no_duplicate_events_after_failure(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
    setup_integration: MockConfigEntry,
) -> None:
    """A failed refresh keeps the baseline.

    On recovery only albums imported during the outage are announced, not
    the whole list.
    """
    album_events = async_capture_events(hass, EVENT_NEW_ALBUM)

    aioclient_mock.clear_requests()
    aioclient_mock.get("http://lidarr.local:8686/api/v1/history", status=500)
    await _refresh(hass, setup_integration)
    assert not setup_integration.runtime_data.coordinator.last_update_success

    aioclient_mock.clear_requests()
    mock_lidarr(
        aioclient_mock,
        history=[history_record(99, 50, "2026-10-19T10:00:00Z"), *default_history()],
    )
    await _refresh(hass, setup_integration)
    assert setup_integration.runtime_data.coordinator.last_update_success
    assert [event.data["album"] for event in album_events] == ["Album 50"]


async def test_no_events_after_reload(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
    setup_integration: MockConfigEntry,
) -> None:
    """A reload starts a new baseline instead of announcing everything."""
    album_events = async_capture_events(hass, EVENT_NEW_ALBUM)
    aioclient_mock.clear_requests()
    mock_lidarr(
        aioclient_mock,
        history=[history_record(99, 50, "2026-10-19T10:00:00Z"), *default_history()],
    )
    assert await hass.config_entries.async_reload(setup_integration.entry_id)
    await hass.async_block_till_done()

    assert album_events == []
