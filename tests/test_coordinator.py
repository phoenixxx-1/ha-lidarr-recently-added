"""Tests for data processing: album grouping, artist sorting, pagination."""

from __future__ import annotations

import itertools
from unittest.mock import patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.test_util.aiohttp import (
    AiohttpClientMocker,
)

from custom_components.lidarr_recently_added.const import (
    CONF_MAX_ALBUMS,
    CONF_MAX_ARTISTS,
    CONF_MAX_ITEMS,
)
from custom_components.lidarr_recently_added.coordinator import (
    ARTIST_IMAGE_TYPES,
    ImageRef,
    build_album_items,
    build_artist_items,
    group_history_by_album,
    pick_image,
)
from homeassistant.core import HomeAssistant

from .conftest import (
    URL,
    album_details,
    artist_entry,
    artist_images,
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


def describe(image: ImageRef | None) -> str | None:
    """Stand-in for the coordinator's URL signer in unit tests."""
    if image is None:
        return None
    return f"{image.kind}/{image.item_id}/{image.filename}@{image.version}"


def test_build_album_items_fields() -> None:
    """Album details are merged in and the cached cover is used."""
    record = history_record(1, 7, "2026-10-18T20:00:00Z", artist="Alpha")
    items = build_album_items([record], {7: album_details(7, total_tracks=14)}, URL)

    assert items[0].as_dict(describe) == {
        "artist": "Alpha",
        "album": "Album 7",
        "release_date": "2024-05-17",
        "added": "2026-10-18T20:00:00+00:00",
        "cover_url": "album/7/cover-500.jpg@42",
        "album_type": "Album",
        "track_count": 14,
        "musicbrainz_id": "mb-album-7",
        "lidarr_url": f"{URL}/album/mb-album-7",
    }


def test_build_album_items_without_details() -> None:
    """Missing details fall back to the embedded album and its cover."""
    record = history_record(1, 7, "2026-10-18T20:00:00Z")
    item = build_album_items([record], {}, URL)[0]

    assert item.album == "Album 7"
    assert item.track_count is None
    # History isn't mapped to Lidarr's cache, so there is no lastWrite.
    assert item.cover == ImageRef("album", 7, "cover-500.jpg", None)


def test_build_album_items_without_images() -> None:
    """An album with no images at all has no cover."""
    record = history_record(1, 7, "2026-10-18T20:00:00Z")
    record["album"]["images"] = []
    item = build_album_items([record], {7: {**album_details(7), "images": []}}, URL)[0]
    assert item.cover is None


def test_build_artist_items_sorted_and_limited() -> None:
    """Artists are sorted by added date, newest first, and cut to N."""
    items = build_artist_items(default_artists(), 3, URL)

    assert [item.artist_id for item in items] == [2, 4, 3]
    assert items[0].as_dict(describe) == {
        "artist": "Newest",
        "added": "2026-10-18T12:00:00+00:00",
        "image_url": "artist/2/poster-500.jpg@63",
        "album_count": 3,
        "musicbrainz_id": "mb-artist-2",
        "lidarr_url": f"{URL}/artist/mb-artist-2",
    }


def test_link_base_url() -> None:
    """Links use the separate link address when one is given."""
    link = "https://lidarr.example.com"
    album = build_album_items([history_record(1, 7, "2026-10-18T20:00:00Z")], {}, link)[
        0
    ]
    artist = build_artist_items(default_artists(), 1, link)[0]
    assert album.lidarr_url == f"{link}/album/mb-album-7"
    assert artist.lidarr_url == f"{link}/artist/mb-artist-2"


@pytest.mark.parametrize(
    ("shape", "expected"),
    [
        # Public https URLs (images.lidarr.audio, TheAudioDB).
        ("remote", ImageRef("artist", 9, "poster-500.jpg", "63")),
        # remoteUrl is a file path inside Lidarr: still a cached image.
        ("local", ImageRef("artist", 9, "poster-500.jpg", "63")),
        # Nothing at all: the card shows initials.
        ("none", None),
    ],
)
def test_pick_image_shapes(shape: str, expected: ImageRef | None) -> None:
    """Every image Lidarr lists is usable, whatever remoteUrl holds."""
    images = artist_images(9, shape)
    assert pick_image("artist", 9, images, ARTIST_IMAGE_TYPES) == expected


@pytest.mark.parametrize(
    ("types", "expected"),
    [
        (("poster", "fanart", "banner", "clearlogo"), "poster-500.jpg"),
        (("fanart", "banner", "clearlogo"), "fanart-360.jpg"),
        (("banner", "clearlogo"), "banner.jpg"),
        # A transparent wordmark looks wrong in a circle: no image instead.
        (("clearlogo",), None),
    ],
)
def test_pick_image_artist_fallback_order(
    types: tuple[str, ...], expected: str | None
) -> None:
    """Artists fall back poster, fanart, banner, and never use clearlogo."""
    images = [i for i in artist_images(9, "local") if i["coverType"] in types]
    image = pick_image("artist", 9, images, ARTIST_IMAGE_TYPES)
    assert (image.filename if image else None) == expected


@pytest.mark.parametrize(
    ("image", "filename", "version"),
    [
        # Mapped to the cache: extension and lastWrite come from the URL.
        (
            {
                "coverType": "Poster",
                "url": "/lidarr/MediaCover/9/poster.png?lastWrite=7",
            },
            "poster-500.png",
            "7",
        ),
        # Unmapped: the extension field, then the remote URL.
        ({"coverType": "poster", "extension": ".gif"}, "poster-500.gif", None),
        (
            {"coverType": "poster", "remoteUrl": "https://x.test/a/b.png?size=1"},
            "poster-500.png",
            None,
        ),
        # Extensions Lidarr's route can't serve fall back to .jpg.
        ({"coverType": "poster", "extension": ".jpeg"}, "poster-500.jpg", None),
        ({"coverType": "poster"}, "poster-500.jpg", None),
    ],
)
def test_pick_image_filename(image: dict, filename: str, version: str | None) -> None:
    """The filename matches what Lidarr's cover route serves."""
    assert pick_image("artist", 9, [image], ARTIST_IMAGE_TYPES) == ImageRef(
        "artist", 9, filename, version
    )


def test_pick_image_ignores_junk() -> None:
    """Malformed image lists don't break anything."""
    assert pick_image("artist", 9, None, ARTIST_IMAGE_TYPES) is None
    assert pick_image("artist", 9, ["x", {"coverType": 3}], ARTIST_IMAGE_TYPES) is None


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


async def test_separate_album_and_artist_counts(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Albums and artists are limited separately."""
    mock_lidarr(aioclient_mock)
    mock_config_entry.add_to_hass(hass)
    hass.config_entries.async_update_entry(
        mock_config_entry, options={CONF_MAX_ALBUMS: 1, CONF_MAX_ARTISTS: 3}
    )
    assert await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    data = mock_config_entry.runtime_data.coordinator.data
    assert [item.album_id for item in data.albums] == [1]
    assert [item.artist_id for item in data.artists] == [2, 4, 3]
