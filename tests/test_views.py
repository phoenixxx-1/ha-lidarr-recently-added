"""Tests for the image proxy view."""

from __future__ import annotations

from http import HTTPStatus
from unittest.mock import patch

import aiohttp
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.test_util.aiohttp import (
    AiohttpClientMocker,
)
from pytest_homeassistant_custom_component.typing import ClientSessionGenerator

from homeassistant.core import HomeAssistant

from .conftest import API_KEY, URL, image_path

JPEG = b"\xff\xd8\xff\xe0" + b"cover-bytes" * 100
LIDARR_POSTER = f"{URL}/api/v1/mediacover/artist/4/poster-500.jpg"


def _artist_image_url(hass: HomeAssistant, index: int) -> str:
    items = hass.states.get("sensor.lidarr_recently_added_artists").attributes["items"]
    return items[index]["image_url"]


async def test_signed_url_serves_image(
    hass: HomeAssistant,
    hass_client_no_auth: ClientSessionGenerator,
    aioclient_mock: AiohttpClientMocker,
    setup_integration: MockConfigEntry,
) -> None:
    """A signed URL from an attribute loads without a token, key stays server-side."""
    aioclient_mock.get(
        LIDARR_POSTER, content=JPEG, headers={"Content-Type": "image/jpeg"}
    )
    # Artist 4's remoteUrl is a path inside Lidarr's container.
    url = _artist_image_url(hass, 1)

    client = await hass_client_no_auth()
    response = await client.get(url)

    assert response.status == HTTPStatus.OK
    assert response.content_type == "image/jpeg"
    assert response.headers["Cache-Control"] == "private, max-age=86400"
    body = await response.read()
    assert body == JPEG

    # Fetched from Lidarr's API-key route, with the key in a header only.
    _, lidarr_url, _, headers = aioclient_mock.mock_calls[-1]
    assert str(lidarr_url) == LIDARR_POSTER
    assert headers["X-Api-Key"] == API_KEY
    assert API_KEY not in str(lidarr_url)
    # Nothing about the key or Lidarr's address reaches the browser.
    assert API_KEY not in str(dict(response.headers))
    assert API_KEY.encode() not in body
    assert "lidarr.local" not in str(dict(response.headers))


async def test_requires_auth(
    hass: HomeAssistant,
    hass_client_no_auth: ClientSessionGenerator,
    aioclient_mock: AiohttpClientMocker,
    setup_integration: MockConfigEntry,
) -> None:
    """Without a token or a valid signature the view refuses."""
    calls_before = len(aioclient_mock.mock_calls)
    client = await hass_client_no_auth()
    path = image_path(setup_integration.entry_id, "artist", 4, "poster-500.jpg")

    response = await client.get(path)
    assert response.status == HTTPStatus.UNAUTHORIZED

    # A signature for one image can't be reused for another.
    signed = _artist_image_url(hass, 1)
    tampered = signed.replace("/artist/4/", "/artist/2/")
    response = await client.get(tampered)
    assert response.status == HTTPStatus.UNAUTHORIZED

    assert len(aioclient_mock.mock_calls) == calls_before


async def test_logged_in_user_can_fetch(
    hass: HomeAssistant,
    hass_client: ClientSessionGenerator,
    aioclient_mock: AiohttpClientMocker,
    setup_integration: MockConfigEntry,
) -> None:
    """A normal authenticated request works without a signature."""
    aioclient_mock.get(
        LIDARR_POSTER, content=JPEG, headers={"Content-Type": "image/jpeg"}
    )
    client = await hass_client()
    path = image_path(setup_integration.entry_id, "artist", 4, "poster-500.jpg")
    response = await client.get(path)
    assert response.status == HTTPStatus.OK


@pytest.mark.parametrize(
    ("mock_kwargs", "status"),
    [
        # Lidarr never cached this image: pass the 404 on.
        ({"status": 404}, HTTPStatus.NOT_FOUND),
        # Lidarr down or misbehaving: a gateway error, not a crash.
        ({"status": 500}, HTTPStatus.BAD_GATEWAY),
        ({"exc": aiohttp.ClientConnectionError()}, HTTPStatus.BAD_GATEWAY),
        ({"status": 401}, HTTPStatus.BAD_GATEWAY),
        (
            {"text": "<html>login</html>", "headers": {"Content-Type": "text/html"}},
            HTTPStatus.BAD_GATEWAY,
        ),
    ],
)
async def test_upstream_errors(
    hass: HomeAssistant,
    hass_client: ClientSessionGenerator,
    aioclient_mock: AiohttpClientMocker,
    setup_integration: MockConfigEntry,
    mock_kwargs: dict,
    status: HTTPStatus,
) -> None:
    """Lidarr's errors map to sensible responses and never leak the key."""
    aioclient_mock.get(LIDARR_POSTER, **mock_kwargs)
    client = await hass_client()
    path = image_path(setup_integration.entry_id, "artist", 4, "poster-500.jpg")
    response = await client.get(path)
    assert response.status == status
    assert API_KEY not in await response.text()


async def test_image_too_large(
    hass: HomeAssistant,
    hass_client: ClientSessionGenerator,
    aioclient_mock: AiohttpClientMocker,
    setup_integration: MockConfigEntry,
) -> None:
    """Oversized responses are refused rather than held in memory."""
    aioclient_mock.get(
        LIDARR_POSTER, content=JPEG, headers={"Content-Type": "image/jpeg"}
    )
    client = await hass_client()
    path = image_path(setup_integration.entry_id, "artist", 4, "poster-500.jpg")
    with patch("custom_components.lidarr_recently_added.api.MAX_IMAGE_BYTES", 100):
        response = await client.get(path)
    assert response.status == HTTPStatus.BAD_GATEWAY


@pytest.mark.parametrize(
    "path_parts",
    [
        ("track", "4", "poster-500.jpg"),
        ("artist", "abc", "poster-500.jpg"),
        ("artist", "4", "poster-500.jpg.exe"),
        ("artist", "4", "clearlogo.png"),
        ("artist", "4", "..%2Fsecrets.yaml"),
        ("artist", "4", "poster-12345.jpg"),
    ],
)
async def test_rejects_unexpected_paths(
    hass: HomeAssistant,
    hass_client: ClientSessionGenerator,
    aioclient_mock: AiohttpClientMocker,
    setup_integration: MockConfigEntry,
    path_parts: tuple[str, str, str],
) -> None:
    """Only the image files the integration links to are proxied."""
    calls_before = len(aioclient_mock.mock_calls)
    client = await hass_client()
    kind, item_id, filename = path_parts
    response = await client.get(
        f"/api/lidarr_recently_added/image/{setup_integration.entry_id}/"
        f"{kind}/{item_id}/{filename}"
    )
    # Path tricks are stopped by Home Assistant's own filter (400) first.
    assert response.status in (HTTPStatus.NOT_FOUND, HTTPStatus.BAD_REQUEST)
    assert len(aioclient_mock.mock_calls) == calls_before


async def test_unknown_or_unloaded_entry(
    hass: HomeAssistant,
    hass_client: ClientSessionGenerator,
    setup_integration: MockConfigEntry,
) -> None:
    """Unknown entries and unloaded entries give 404."""
    client = await hass_client()
    response = await client.get(image_path("nope", "artist", 4, "poster-500.jpg"))
    assert response.status == HTTPStatus.NOT_FOUND

    other = MockConfigEntry(domain="other_domain")
    other.add_to_hass(hass)
    response = await client.get(image_path(other.entry_id, "artist", 4, "poster.jpg"))
    assert response.status == HTTPStatus.NOT_FOUND

    assert await hass.config_entries.async_unload(setup_integration.entry_id)
    path = image_path(setup_integration.entry_id, "artist", 4, "poster-500.jpg")
    response = await client.get(path)
    assert response.status == HTTPStatus.NOT_FOUND
