"""Data update coordinator for Lidarr Recently Added."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import heapq
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import CALLBACK_TYPE, HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .api import LidarrAuthenticationError, LidarrClient, LidarrError
from .const import (
    CONF_ALBUMS_ENABLED,
    CONF_ARTISTS_ENABLED,
    CONF_MAX_ITEMS,
    CONF_SCAN_INTERVAL,
    DEFAULT_MAX_ITEMS,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    EVENT_NEW_ALBUM,
    EVENT_NEW_ARTIST,
    HISTORY_IMPORT_EVENT_TYPES,
    HISTORY_MAX_PAGES,
    HISTORY_PAGE_SIZE,
    LOGGER,
)

type LidarrRecentlyAddedConfigEntry = ConfigEntry[LidarrRecentlyAddedRuntimeData]

ALBUM_COVER_TYPES = ("cover", "disc")
ARTIST_IMAGE_TYPES = ("poster", "fanart")


@dataclass(frozen=True, slots=True)
class AlbumItem:
    """A recently imported album."""

    album_id: int
    artist: str | None
    album: str | None
    release_date: str | None
    added: datetime
    cover_url: str | None
    album_type: str | None
    track_count: int | None
    musicbrainz_id: str | None
    lidarr_url: str | None

    @property
    def title(self) -> str | None:
        """Return "Artist – Album", or whichever part is known."""
        parts = [part for part in (self.artist, self.album) if part]
        return " – ".join(parts) or None

    @property
    def picture_url(self) -> str | None:
        """Return the public cover image URL."""
        return self.cover_url

    def as_dict(self) -> dict[str, Any]:
        """Return the public, JSON-serialisable representation."""
        return {
            "artist": self.artist,
            "album": self.album,
            "release_date": self.release_date,
            "added": self.added.isoformat(),
            "cover_url": self.cover_url,
            "album_type": self.album_type,
            "track_count": self.track_count,
            "musicbrainz_id": self.musicbrainz_id,
            "lidarr_url": self.lidarr_url,
        }


@dataclass(frozen=True, slots=True)
class ArtistItem:
    """A recently added artist."""

    artist_id: int
    artist: str | None
    added: datetime
    image_url: str | None
    album_count: int | None
    musicbrainz_id: str | None
    lidarr_url: str | None

    @property
    def title(self) -> str | None:
        """Return the artist name."""
        return self.artist

    @property
    def picture_url(self) -> str | None:
        """Return the public artist image URL."""
        return self.image_url

    def as_dict(self) -> dict[str, Any]:
        """Return the public, JSON-serialisable representation."""
        return {
            "artist": self.artist,
            "added": self.added.isoformat(),
            "image_url": self.image_url,
            "album_count": self.album_count,
            "musicbrainz_id": self.musicbrainz_id,
            "lidarr_url": self.lidarr_url,
        }


@dataclass(slots=True)
class RecentlyAddedData:
    """Result of one refresh. None means the sensor type is disabled."""

    albums: list[AlbumItem] | None
    artists: list[ArtistItem] | None


@dataclass(slots=True)
class LidarrRecentlyAddedRuntimeData:
    """Runtime data stored on the config entry."""

    coordinator: LidarrRecentlyAddedCoordinator
    system_status: dict[str, Any] = field(default_factory=dict)


def _parse_datetime(value: Any) -> datetime | None:
    """Parse a Lidarr timestamp. Lidarr sends UTC; treat naive values as UTC."""
    if not isinstance(value, str):
        return None
    parsed = dt_util.parse_datetime(value)
    if parsed is None:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt_util.UTC)
    return parsed


def _parse_date(value: Any) -> str | None:
    """Return the date part of a Lidarr timestamp as YYYY-MM-DD."""
    parsed = _parse_datetime(value)
    return parsed.date().isoformat() if parsed else None


def _public_image_url(images: Any, cover_types: Iterable[str]) -> str | None:
    """Pick the first public remote image URL matching the preferred types.

    Only absolute http(s) URLs are returned. The local /MediaCover paths
    need Lidarr credentials, so they are never used.
    """
    if not isinstance(images, list):
        return None
    by_type: dict[str, str] = {}
    for image in images:
        if not isinstance(image, Mapping):
            continue
        remote = image.get("remoteUrl")
        cover_type = image.get("coverType")
        if (
            isinstance(remote, str)
            and isinstance(cover_type, str)
            and remote.lower().startswith(("https://", "http://"))
        ):
            by_type.setdefault(cover_type.lower(), remote)
    for cover_type in cover_types:
        if cover_type in by_type:
            return by_type[cover_type]
    return None


def _int_or_none(value: Any) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def _str_or_none(value: Any) -> str | None:
    return value if isinstance(value, str) and value else None


def group_history_by_album(
    records: Iterable[Mapping[str, Any]], seen: dict[int, Mapping[str, Any]]
) -> None:
    """Add the newest import record per album to ``seen``.

    Records must arrive newest first, so the first record seen for an album
    holds its latest import time. ``seen`` keeps insertion order, which is
    therefore newest-first by latest import.
    """
    for record in records:
        album_id = record.get("albumId")
        if not isinstance(album_id, int) or album_id <= 0 or album_id in seen:
            continue
        if _parse_datetime(record.get("date")) is None:
            continue
        seen[album_id] = record


def build_album_items(
    history: Iterable[Mapping[str, Any]],
    albums_by_id: Mapping[int, Mapping[str, Any]],
    base_url: str,
) -> list[AlbumItem]:
    """Build album items from grouped history records and album details."""
    items: list[AlbumItem] = []
    for record in history:
        album_id: int = record["albumId"]
        added = _parse_datetime(record.get("date"))
        if added is None:
            continue
        # The album embedded in history has no statistics; the album endpoint
        # does. Prefer the endpoint's values, keep the embedded ones as backup.
        embedded = record.get("album")
        album: dict[str, Any] = {
            **(embedded if isinstance(embedded, Mapping) else {}),
            **albums_by_id.get(album_id, {}),
        }
        artist = record.get("artist")
        artist_name = (
            _str_or_none(artist.get("artistName"))
            if isinstance(artist, Mapping)
            else None
        )
        if artist_name is None and isinstance(album.get("artist"), Mapping):
            artist_name = _str_or_none(album["artist"].get("artistName"))

        statistics = album.get("statistics")
        track_count = None
        if isinstance(statistics, Mapping):
            track_count = _int_or_none(statistics.get("totalTrackCount"))
            if track_count is None:
                track_count = _int_or_none(statistics.get("trackCount"))

        foreign_id = _str_or_none(album.get("foreignAlbumId"))
        items.append(
            AlbumItem(
                album_id=album_id,
                artist=artist_name,
                album=_str_or_none(album.get("title")),
                release_date=_parse_date(album.get("releaseDate")),
                added=added,
                cover_url=_public_image_url(album.get("images"), ALBUM_COVER_TYPES),
                album_type=_str_or_none(album.get("albumType")),
                track_count=track_count,
                musicbrainz_id=foreign_id,
                lidarr_url=f"{base_url}/album/{foreign_id}" if foreign_id else None,
            )
        )
    return items


def build_artist_items(
    artists: Iterable[Mapping[str, Any]], max_items: int, base_url: str
) -> list[ArtistItem]:
    """Return the ``max_items`` most recently added artists, newest first."""
    dated: list[tuple[datetime, Mapping[str, Any]]] = []
    for artist in artists:
        if not isinstance(artist, Mapping) or not isinstance(artist.get("id"), int):
            continue
        added = _parse_datetime(artist.get("added"))
        if added is not None:
            dated.append((added, artist))

    newest = heapq.nlargest(max_items, dated, key=lambda pair: pair[0])
    items: list[ArtistItem] = []
    for added, artist in newest:
        statistics = artist.get("statistics")
        foreign_id = _str_or_none(artist.get("foreignArtistId"))
        image_url = _public_image_url(artist.get("images"), ARTIST_IMAGE_TYPES)
        remote_poster = artist.get("remotePoster")
        if (
            image_url is None
            and isinstance(remote_poster, str)
            and remote_poster.lower().startswith(("https://", "http://"))
        ):
            image_url = remote_poster
        items.append(
            ArtistItem(
                artist_id=artist["id"],
                artist=_str_or_none(artist.get("artistName")),
                added=added,
                image_url=image_url,
                album_count=(
                    _int_or_none(statistics.get("albumCount"))
                    if isinstance(statistics, Mapping)
                    else None
                ),
                musicbrainz_id=foreign_id,
                lidarr_url=f"{base_url}/artist/{foreign_id}" if foreign_id else None,
            )
        )
    return items


class LidarrRecentlyAddedCoordinator(DataUpdateCoordinator[RecentlyAddedData]):
    """Fetch recently added albums and artists from Lidarr."""

    config_entry: LidarrRecentlyAddedConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: LidarrRecentlyAddedConfigEntry,
        client: LidarrClient,
    ) -> None:
        """Initialise the coordinator."""
        options = config_entry.options
        super().__init__(
            hass,
            LOGGER,
            config_entry=config_entry,
            name=DOMAIN,
            update_interval=timedelta(
                minutes=options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
            ),
        )
        self.client = client
        self.max_items: int = options.get(CONF_MAX_ITEMS, DEFAULT_MAX_ITEMS)
        self.albums_enabled: bool = options.get(CONF_ALBUMS_ENABLED, True)
        self.artists_enabled: bool = options.get(CONF_ARTISTS_ENABLED, True)
        # IDs from the last successful refresh. None until the first one, so
        # the initial list is never announced as new.
        self._known_album_ids: set[int] | None = None
        self._known_artist_ids: set[int] | None = None
        self._pending_events: list[tuple[str, dict[str, Any]]] = []

    async def _async_update_data(self) -> RecentlyAddedData:
        """Fetch and process data from Lidarr."""
        try:
            albums = await self._async_fetch_albums() if self.albums_enabled else None
            artists = (
                await self._async_fetch_artists() if self.artists_enabled else None
            )
        except LidarrAuthenticationError as err:
            raise ConfigEntryAuthFailed(str(err)) from err
        except LidarrError as err:
            raise UpdateFailed(str(err)) from err

        self._queue_new_item_events(albums, artists)
        return RecentlyAddedData(albums=albums, artists=artists)

    async def _async_fetch_albums(self) -> list[AlbumItem]:
        """Fetch enough history pages to fill ``max_items`` distinct albums."""
        seen: dict[int, Mapping[str, Any]] = {}
        for page in range(1, HISTORY_MAX_PAGES + 1):
            data = await self.client.async_get_history_page(
                page, HISTORY_PAGE_SIZE, HISTORY_IMPORT_EVENT_TYPES
            )
            records = data.get("records")
            if not isinstance(records, list):
                break
            group_history_by_album(records, seen)
            total = data.get("totalRecords")
            if (
                len(seen) >= self.max_items
                or not records
                or not isinstance(total, int)
                or page * HISTORY_PAGE_SIZE >= total
            ):
                break

        newest = list(seen.values())[: self.max_items]
        details = await self.client.async_get_albums(
            record["albumId"] for record in newest
        )
        albums_by_id = {
            album["id"]: album
            for album in details
            if isinstance(album, Mapping) and isinstance(album.get("id"), int)
        }
        return build_album_items(newest, albums_by_id, self.client.base_url)

    async def _async_fetch_artists(self) -> list[ArtistItem]:
        """Fetch the library and keep only the newest ``max_items`` artists."""
        artists = await self.client.async_get_artists()
        return build_artist_items(artists, self.max_items, self.client.base_url)

    def _queue_new_item_events(
        self, albums: list[AlbumItem] | None, artists: list[ArtistItem] | None
    ) -> None:
        """Work out which items are new since the last successful refresh."""
        if albums is not None:
            ids = {item.album_id for item in albums}
            if self._known_album_ids is not None:
                self._pending_events.extend(
                    (EVENT_NEW_ALBUM, item.as_dict())
                    for item in reversed(albums)
                    if item.album_id not in self._known_album_ids
                )
            self._known_album_ids = ids
        if artists is not None:
            ids = {item.artist_id for item in artists}
            if self._known_artist_ids is not None:
                self._pending_events.extend(
                    (EVENT_NEW_ARTIST, item.as_dict())
                    for item in reversed(artists)
                    if item.artist_id not in self._known_artist_ids
                )
            self._known_artist_ids = ids

    @callback
    def async_fire_pending_events(self) -> None:
        """Fire queued events, oldest first.

        Registered as a coordinator listener so events fire after the new
        data is stored, and therefore see the same state as the sensors.
        """
        events, self._pending_events = self._pending_events, []
        for event_type, item in events:
            self.hass.bus.async_fire(
                event_type, {**item, "config_entry_id": self.config_entry.entry_id}
            )

    @callback
    def async_start_event_listener(self) -> CALLBACK_TYPE:
        """Start firing events after each refresh. Returns the unsubscribe."""
        return self.async_add_listener(self.async_fire_pending_events)
