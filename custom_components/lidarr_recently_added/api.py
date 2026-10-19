"""Minimal async client for the parts of the Lidarr v1 API this integration uses."""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Iterable, Sequence
from typing import Any

import aiohttp
from yarl import URL

from .const import MAX_IMAGE_BYTES, REQUEST_TIMEOUT


class LidarrError(Exception):
    """Base error talking to Lidarr."""


class LidarrConnectionError(LidarrError):
    """Lidarr could not be reached or returned an unexpected response."""


class LidarrAuthenticationError(LidarrError):
    """Lidarr rejected the API key."""


class LidarrNotFoundError(LidarrError):
    """Lidarr has no such resource, for example a cover it never cached."""


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

    async def _request[T](
        self,
        path: str,
        params: Sequence[tuple[str, str | int]] | None,
        accept: str,
        read: Callable[[aiohttp.ClientResponse], Awaitable[T]],
    ) -> T:
        """GET a path under /api/v1 and return what ``read`` makes of the reply."""
        url = f"{self._base_url}/api/v1/{path}"
        try:
            async with self._session.get(
                url,
                params=params,
                headers={"X-Api-Key": self._api_key, "Accept": accept},
                timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT),
                # aiohttp keeps custom headers across redirects, so following
                # one could hand the API key to another host.
                allow_redirects=False,
            ) as response:
                if response.status in (401, 403):
                    raise LidarrAuthenticationError(
                        f"Lidarr rejected the API key (HTTP {response.status})"
                    )
                if response.status == 404:
                    raise LidarrNotFoundError(f"Not found: {path}")
                if not 200 <= response.status < 300:
                    raise LidarrConnectionError(
                        f"Unexpected HTTP {response.status} from {path}"
                    )
                return await read(response)
        except (aiohttp.ClientError, TimeoutError) as err:
            raise LidarrConnectionError(
                f"Error communicating with Lidarr: {err.__class__.__name__}"
            ) from err

    async def _get(
        self, path: str, params: Sequence[tuple[str, str | int]] | None = None
    ) -> Any:
        """GET a path under /api/v1 and return the decoded JSON."""

        async def read_json(response: aiohttp.ClientResponse) -> Any:
            try:
                return await response.json(content_type=None)
            except ValueError as err:
                raise LidarrConnectionError(f"Invalid JSON from {path}") from err

        return await self._request(path, params, "application/json", read_json)

    async def async_get_media_cover(
        self, kind: str, item_id: int, filename: str
    ) -> tuple[bytes, str]:
        """Return the bytes and content type of a cached artist or album image.

        Uses the API-key route, /api/v1/mediacover/{kind}/{id}/{filename}.
        Lidarr serves the full-size file when a resized one doesn't exist.
        """
        path = f"mediacover/{kind}/{item_id}/{filename}"

        async def read_image(response: aiohttp.ClientResponse) -> tuple[bytes, str]:
            content_type = (response.headers.get("Content-Type") or "").split(";")[0]
            if not content_type.startswith("image/"):
                raise LidarrConnectionError(f"Not an image: {path}")
            length = response.headers.get("Content-Length")
            if length and length.isdecimal() and int(length) > MAX_IMAGE_BYTES:
                raise LidarrConnectionError(f"Image too large: {path}")
            chunks: list[bytes] = []
            size = 0
            async for chunk in response.content.iter_chunked(64 * 1024):
                size += len(chunk)
                if size > MAX_IMAGE_BYTES:
                    raise LidarrConnectionError(f"Image too large: {path}")
                chunks.append(chunk)
            return b"".join(chunks), content_type

        return await self._request(path, None, "image/*", read_image)

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
