"""Authenticated image proxy for Lidarr artwork."""

from __future__ import annotations

from http import HTTPStatus
import re

from aiohttp import web

from homeassistant.components.http import KEY_HASS, HomeAssistantView
from homeassistant.config_entries import ConfigEntryState

from .api import LidarrError, LidarrNotFoundError
from .const import DOMAIN, IMAGE_VIEW_URL, LOGGER
from .coordinator import LidarrRecentlyAddedConfigEntry

# Only the files the integration itself links to: an image type, an optional
# resized height, and one of the extensions Lidarr's cover route serves.
_FILENAME = re.compile(r"^(poster|fanart|banner|cover|disc)(-\d{2,3})?\.(jpg|png|gif)$")
_KINDS = frozenset({"artist", "album"})

CACHE_CONTROL = "private, max-age=86400"


class LidarrImageView(HomeAssistantView):
    """Serve artist and album images from Lidarr's cover cache.

    Home Assistant fetches the file with the API key and passes the bytes on,
    so the key never reaches the browser and every image comes from Home
    Assistant's own origin. Browsers load these URLs through signed paths.
    """

    url = IMAGE_VIEW_URL + "/{entry_id}/{kind}/{item_id}/{filename}"
    name = "api:lidarr_recently_added:image"
    requires_auth = True

    async def get(
        self,
        request: web.Request,
        entry_id: str,
        kind: str,
        item_id: str,
        filename: str,
    ) -> web.StreamResponse:
        """Return one image."""
        if (
            kind not in _KINDS
            or not item_id.isdecimal()
            or not _FILENAME.match(filename)
        ):
            return web.Response(status=HTTPStatus.NOT_FOUND)

        hass = request.app[KEY_HASS]
        entry: LidarrRecentlyAddedConfigEntry | None = (
            hass.config_entries.async_get_entry(entry_id)
        )
        if (
            entry is None
            or entry.domain != DOMAIN
            or entry.state is not ConfigEntryState.LOADED
        ):
            return web.Response(status=HTTPStatus.NOT_FOUND)

        client = entry.runtime_data.coordinator.client
        try:
            body, content_type = await client.async_get_media_cover(
                kind, int(item_id), filename
            )
        except LidarrNotFoundError:
            return web.Response(status=HTTPStatus.NOT_FOUND)
        except LidarrError as err:
            LOGGER.debug("Couldn't fetch %s %s %s: %s", kind, item_id, filename, err)
            return web.Response(status=HTTPStatus.BAD_GATEWAY)

        return web.Response(
            body=body,
            content_type=content_type,
            headers={"Cache-Control": CACHE_CONTROL},
        )
