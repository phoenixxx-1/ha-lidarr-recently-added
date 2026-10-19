"""Tests for data processing: album grouping, artist sorting, pagination."""

from __future__ import annotations

import itertools
from unittest.mock import patch

from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.test_util.aiohttp import (
    AiohttpClientMocker,
)

from custom_components.lidarr_recently_added.const import CONF_MAX_ITEMS
from custom_components.lidarr_recently_added.coordinator import (
    build_album_items,
    build_artist_items,
    group_history_by_album,
)
from homeassistant.core import HomeAssistant

from .conftest import (
    URL,
    album_details,
    artist_entry,
    default_artists,
    default_history,
    history_record,
    mock_lidarr,
)


def test_group_history_by_album_keeps_latest_import() -> None:
    """Per-track events collapse to one entry per album, newest first."""
    seen: dict = {}
    group_history_by_album(default_history(), seen)

    assert list(seen) == [1, 2, 3]
    assert seen[1]["date"] == "2026-10-18T20:00:03Z"
    assert seen[2]["date"] == "2026-10-17T10:00:00Z"


def test_group_history_skips_bad_records() -> None:
    """Records without a usable album ID or date are ignored."""
    seen: dict = {}
    good = history_record(1, 5, "2026-10-01T00:00:00Z")
    group_history_by_album(
        [
            {**good, "albumId": 0},
            {**good, "albumId": None},
            {**good, "date": None},
            {**good, "date": "not a date"},
            good,
        ],
        seen,
    )
    assert list(seen) == [5]


def test_group_history_across_pages() -> None:
    """An album seen on page 1 isn't moved by older events on page 2."""
    seen: dict = {}
    group_history_by_album([history_record(3, 1, "2026-10-03T00:00:00Z")], seen)
    group_history_by_album(
        [
            history_record(2, 1, "2026-10-02T00:00:00Z"),
            history_record(1, 2, "2026-10-01T00:00:00Z"),
        ],
        seen,
    )
    assert list(seen) == [1, 2]
    assert seen[1]["id"] == 3


def test_build_album_items_fields() -> None:
    """Album details are merged in and only public URLs are used."""
    record = history_record(1, 7, "2026-10-18T20:00:00Z", artist="Alpha")
    items = build_album_items([record], {7: album_details(7, total_tracks=14)}, URL)

    assert items[0].as_dict() == {
        "artist": "Alpha",
        "album": "Album 7",
        "release_date": "2024-05-17",
        "added": "2026-10-18T20:00:00+00:00",
        "cover_url": "https://coverartarchive.org/release/7/front.jpg",
        "album_type": "Album",
        "track_count": 14,
        "musicbrainz_id": "mb-album-7",
        "lidarr_url": f"{URL}/album/mb-album-7",
    }


def test_build_album_items_without_details_or_remote_url() -> None:
    """Missing details fall back to the embedded album; no remote URL means None."""
    record = history_record(1, 7, "2026-10-18T20:00:00Z")
    record["album"]["images"] = [
        {"url": "/MediaCover/Albums/7/cover.jpg", "coverType": "cover"},
        {"coverType": "disc", "remoteUrl": "/config/MediaCover/local.jpg"},
    ]
    item = build_album_items([record], {}, URL)[0]

    assert item.album == "Album 7"
    assert item.track_count is None
    assert item.cover_url is None


def test_build_artist_items_sorted_and_limited() -> None:
    """Artists are sorted by added date, newest first, and cut to N."""
    items = build_artist_items(default_artists(), 3, URL)

    assert [item.artist_id for item in items] == [2, 4, 3]
    assert items[0].as_dict() == {
        "artist": "Newest",
        "added": "2026-10-18T12:00:00+00:00",
        "image_url": "https://assets.fanart.tv/fanart/2.jpg",
        "album_count": 3,
        "musicbrainz_id": "mb-artist-2",
        "lidarr_url": f"{URL}/artist/mb-artist-2",
    }
    # Artist 4 only has a local MediaCover path, so there is no image.
    assert items[1].image_url is None


def test_build_artist_items_large_library() -> None:
    """Only the newest N survive from a large library."""
    artists = [
        artist_entry(i, f"2020-{1 + i % 12:02d}-{1 + i % 28:02d}T00:00:00Z")
        for i in range(1, 3001)
    ]
    artists.append(artist_entry(9999, "2026-10-19T00:00:00Z"))
    items = build_artist_items(artists, 25, URL)

    assert len(items) == 25
    assert items[0].artist_id == 9999
    assert all(a.added >= b.added for a, b in itertools.pairwise(items))


async def test_fetches_more_pages_until_full(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Pages are fetched until enough distinct albums are found, then stop."""
    # Two pages of five: page 1 is all one album's tracks, page 2 has two more.
    history = [
        history_record(20 - i, 1, f"2026-10-18T20:00:{59 - i:02d}Z", track_id=i)
        for i in range(5)
    ] + [
        history_record(10, 2, "2026-10-17T00:00:00Z"),
        history_record(9, 3, "2026-10-16T00:00:00Z"),
        history_record(8, 3, "2026-10-15T00:00:00Z"),
        history_record(7, 4, "2026-10-14T00:00:00Z"),
        history_record(6, 5, "2026-10-13T00:00:00Z"),
    ]
    mock_lidarr(aioclient_mock, history=history, page_size=5)
    mock_config_entry.add_to_hass(hass)
    hass.config_entries.async_update_entry(
        mock_config_entry, options={CONF_MAX_ITEMS: 3}
    )

    with patch(
        "custom_components.lidarr_recently_added.coordinator.HISTORY_PAGE_SIZE", 5
    ):
        assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
        await hass.async_block_till_done()

    data = mock_config_entry.runtime_data.coordinator.data
    assert [item.album_id for item in data.albums] == [1, 2, 3]

    history_urls = [
        str(c[1]) for c in aioclient_mock.mock_calls if "/history" in str(c[1])
    ]
    assert len(history_urls) == 2
    assert "eventType=3" in history_urls[0]
    assert "eventType=8" in history_urls[0]
    assert "includeAlbum=true" in history_urls[0]

    album_call = next(c for c in aioclient_mock.mock_calls if "/album?" in str(c[1]))
    assert str(album_call[1]).count("albumIds=") == 3
