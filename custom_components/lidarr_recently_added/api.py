"""Minimal async client for the parts of the Lidarr v1 API this integration uses."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import Any

import aiohttp
from yarl import URL

from .const import REQUEST_TIMEOUT


class LidarrError(Exception):
    """Base error talking to Lidarr."""


class LidarrConnectionError(LidarrError):
    """Lidarr could not be reached or returned an unexpected response."""


class LidarrAuthenticationError(LidarrError):
    """Lidarr rejected the API key."""


class InvalidUrlError(ValueError):
    """The URL is not an absolute http(s) URL."""


def normalize_url(url: str) -> str:
    """Return a canonical form of a Lidarr base URL.

    Lower-cases the scheme and host, drops default ports, query strings,
    fragments and trailing slashes, and keeps any base path.
    """
    parsed = URL(url.strip())
    if parsed.scheme not in ("http", "https") or not parsed.host:
        raise InvalidUrlError(url)
    normalized = URL.build(
        scheme=parsed.scheme,
        host=parsed.host.lower(),
        port=parsed.explicit_port if not parsed.is_default_port() else None,
        path=parsed.path.rstrip("/"),
    )
    return str(normalized)


class LidarrClient:
    """Talk to a Lidarr instance using HA's shared aiohttp session."""

    def __init__(self, session: aiohttp.ClientSession, url: str, api_key: str) -> None:
        """Initialise the client."""
        self._session = session
        self._base_url = normalize_url(url)
        self._api_key = api_key

    @property
    def base_url(self) -> str:
        """Return the normalised base URL, without a trailing slash."""
        return self._base_url

    async def _get(
        self, path: str, params: Sequence[tuple[str, str | int]] | None = None
    ) -> Any:
        """Perform a GET request against /api/v1 and return the decoded JSON."""
        url = f"{self._base_url}/api/v1/{path}"
        try:
            async with self._session.get(
                url,
                params=params,
                headers={"X-Api-Key": self._api_key, "Accept": "application/json"},
                timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT),
                # aiohttp keeps custom headers across redirects, so following
                # one could hand the API key to another host.
                allow_redirects=False,
            ) as response:
                if response.status in (401, 403):
                    raise LidarrAuthenticationError(
                        f"Lidarr rejected the API key (HTTP {response.status})"
                    )
                if not 200 <= response.status < 300:
                    raise LidarrConnectionError(
                        f"Unexpected HTTP {response.status} from {path}"
                    )
                return await response.json(content_type=None)
        except (aiohttp.ClientError, TimeoutError) as err:
            raise LidarrConnectionError(
                f"Error communicating with Lidarr: {err.__class__.__name__}"
            ) from err
        except ValueError as err:
            raise LidarrConnectionError(f"Invalid JSON from {path}") from err

    async def async_get_system_status(self) -> dict[str, Any]:
        """Return /system/status."""
        data = await self._get("system/status")
        if not isinstance(data, dict):
            raise LidarrConnectionError("Unexpected system/status response")
        return data

    async def async_get_history_page(
        self, page: int, page_size: int, event_types: Iterable[int]
    ) -> dict[str, Any]:
        """Return one page of history, newest first, with album and artist."""
        params: list[tuple[str, str | int]] = [
            ("page", page),
            ("pageSize", page_size),
            ("sortKey", "date"),
            ("sortDirection", "descending"),
            ("includeAlbum", "true"),
            ("includeArtist", "true"),
        ]
        params.extend(("eventType", event_type) for event_type in event_types)
        data = await self._get("history", params)
        if not isinstance(data, dict):
            raise LidarrConnectionError("Unexpected history response")
        return data

    async def async_get_albums(self, album_ids: Iterable[int]) -> list[dict[str, Any]]:
        """Return the albums with the given IDs, including statistics."""
        params: list[tuple[str, str | int]] = [
            ("albumIds", album_id) for album_id in album_ids
        ]
        if not params:
            return []
        data = await self._get("album", params)
        if not isinstance(data, list):
            raise LidarrConnectionError("Unexpected album response")
        return data

    async def async_get_artists(self) -> list[dict[str, Any]]:
        """Return every artist in the library."""
        data = await self._get("artist")
        if not isinstance(data, list):
            raise LidarrConnectionError("Unexpected artist response")
        return data
