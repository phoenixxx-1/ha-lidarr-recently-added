"""Fixtures for Lidarr Recently Added tests."""

from __future__ import annotations

from typing import Any

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.test_util.aiohttp import (
    AiohttpClientMocker,
)

from custom_components.lidarr_recently_added.const import DOMAIN
from homeassistant.const import CONF_API_KEY, CONF_URL, CONF_VERIFY_SSL
from homeassistant.core import HomeAssistant

URL = "http://lidarr.local:8686"
API_KEY = "0123456789abcdef0123456789abcdef"

SYSTEM_STATUS = {
    "appName": "Lidarr",
    "instanceName": "Lidarr",
    "version": "3.1.2.4913",
    "branch": "develop",
    "osName": "debian",
    "isDocker": True,
    "urlBase": "",
    "appData": "/config",
    "startupPath": "/app/lidarr/bin",
}


def history_record(
    record_id: int,
    album_id: int,
    date: str,
    *,
    artist: str = "Artist",
    title: str | None = None,
    event_type: str = "trackFileImported",
    track_id: int = 0,
) -> dict[str, Any]:
    """Build a history record as returned with includeAlbum/includeArtist."""
    return {
        "id": record_id,
        "albumId": album_id,
        "artistId": album_id * 10,
        "trackId": track_id,
        "sourceTitle": f"{artist} - {title or f'Album {album_id}'}",
        "date": date,
        "eventType": event_type,
        "downloadId": f"dl{album_id}",
        "data": {"importedPath": f"/music/{artist}/{album_id}/01.flac"},
        "album": {
            "id": album_id,
            "title": title or f"Album {album_id}",
            "foreignAlbumId": f"mb-album-{album_id}",
            "releaseDate": "2024-05-17T00:00:00Z",
            "albumType": "Album",
            "images": [
                {
                    "url": f"/MediaCover/Albums/{album_id}/cover.jpg?lastWrite=1",
                    "coverType": "cover",
                    "extension": ".jpg",
                    "remoteUrl": f"https://coverartarchive.org/release/{album_id}/front.jpg",
                }
            ],
        },
        "artist": {
            "id": album_id * 10,
            "artistName": artist,
            "foreignArtistId": f"mb-artist-{album_id * 10}",
        },
    }


def album_details(album_id: int, total_tracks: int = 12) -> dict[str, Any]:
    """Build an /api/v1/album entry with statistics."""
    return {
        "id": album_id,
        "title": f"Album {album_id}",
        "foreignAlbumId": f"mb-album-{album_id}",
        "releaseDate": "2024-05-17T00:00:00Z",
        "albumType": "Album",
        "images": [
            {
                "url": f"/MediaCover/Albums/{album_id}/cover.jpg?lastWrite=1",
                "coverType": "cover",
                "extension": ".jpg",
                "remoteUrl": f"https://coverartarchive.org/release/{album_id}/front.jpg",
            }
        ],
        "statistics": {
            "trackFileCount": total_tracks,
            "trackCount": total_tracks,
            "totalTrackCount": total_tracks,
            "sizeOnDisk": 123456789,
            "percentOfTracks": 100.0,
        },
    }


def artist_entry(
    artist_id: int, added: str, *, name: str | None = None, images: bool = True
) -> dict[str, Any]:
    """Build an /api/v1/artist entry."""
    return {
        "id": artist_id,
        "artistName": name or f"Artist {artist_id}",
        "foreignArtistId": f"mb-artist-{artist_id}",
        "added": added,
        "overview": "x" * 500,
        "images": (
            [
                {
                    "url": f"/MediaCover/{artist_id}/poster.jpg?lastWrite=1",
                    "coverType": "poster",
                    "extension": ".jpg",
                    "remoteUrl": f"https://assets.fanart.tv/fanart/{artist_id}.jpg",
                },
                {
                    "url": f"/MediaCover/{artist_id}/banner.jpg?lastWrite=1",
                    "coverType": "banner",
                    "extension": ".jpg",
                    "remoteUrl": f"https://assets.fanart.tv/banner/{artist_id}.jpg",
                },
            ]
            if images
            else [
                {
                    "url": f"/MediaCover/{artist_id}/poster.jpg?lastWrite=1",
                    "coverType": "poster",
                    "extension": ".jpg",
                }
            ]
        ),
        "statistics": {"albumCount": artist_id % 7 + 1, "trackFileCount": 10},
    }


def default_history() -> list[dict[str, Any]]:
    """Three albums: album 1 imported as 3 per-track events, newest first."""
    return [
        history_record(10, 1, "2026-10-18T20:00:03Z", artist="Alpha", track_id=103),
        history_record(9, 1, "2026-10-18T20:00:02Z", artist="Alpha", track_id=102),
        history_record(8, 1, "2026-10-18T20:00:01Z", artist="Alpha", track_id=101),
        history_record(
            7, 1, "2026-10-18T20:00:00Z", artist="Alpha", event_type="downloadImported"
        ),
        history_record(6, 2, "2026-10-17T10:00:00Z", artist="Bravo", track_id=201),
        history_record(5, 3, "2026-10-16T10:00:00Z", artist="Charlie", track_id=301),
        # An older import of album 2 must not change its position.
        history_record(4, 2, "2026-10-01T10:00:00Z", artist="Bravo", track_id=202),
    ]


def default_artists() -> list[dict[str, Any]]:
    """Artists in library order, deliberately not sorted by added date."""
    return [
        artist_entry(1, "2025-01-01T00:00:00Z"),
        artist_entry(2, "2026-10-18T12:00:00Z", name="Newest"),
        artist_entry(3, "2026-03-01T00:00:00Z"),
        artist_entry(4, "2026-10-10T00:00:00Z", images=False),
        {"id": 5, "artistName": "No date"},
    ]


def mock_lidarr(
    aioclient_mock: AiohttpClientMocker,
    *,
    history: list[dict[str, Any]] | None = None,
    artists: list[dict[str, Any]] | None = None,
    status: dict[str, Any] | None = None,
    page_size: int = 250,
) -> None:
    """Register Lidarr API responses."""
    history = default_history() if history is None else history
    artists = default_artists() if artists is None else artists
    aioclient_mock.get(f"{URL}/api/v1/system/status", json=status or SYSTEM_STATUS)
    pages = [history[i : i + page_size] for i in range(0, len(history), page_size)]
    for number, records in enumerate(pages or [[]], start=1):
        aioclient_mock.get(
            f"{URL}/api/v1/history?page={number}",
            json={
                "page": number,
                "pageSize": page_size,
                "sortKey": "date",
                "sortDirection": "descending",
                "totalRecords": len(history),
                "records": records,
            },
        )
    album_ids = sorted({record["albumId"] for record in history})
    aioclient_mock.get(
        f"{URL}/api/v1/album",
        json=[
            album_details(album_id, total_tracks=10 + album_id)
            for album_id in album_ids
        ],
    )
    aioclient_mock.get(f"{URL}/api/v1/artist", json=artists)


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations: None) -> None:
    """Enable custom integrations in every test."""


@pytest.fixture
def mock_config_entry() -> MockConfigEntry:
    """Return a config entry."""
    return MockConfigEntry(
        domain=DOMAIN,
        title="Lidarr",
        unique_id=URL,
        data={CONF_URL: URL, CONF_API_KEY: API_KEY, CONF_VERIFY_SSL: True},
        options={},
    )


@pytest.fixture
async def setup_integration(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
    mock_config_entry: MockConfigEntry,
) -> MockConfigEntry:
    """Set up the integration with the default mocked data."""
    mock_lidarr(aioclient_mock)
    mock_config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    return mock_config_entry
