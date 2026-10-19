"""Tests for diagnostics."""

from __future__ import annotations

import json

from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.components.diagnostics import (
    get_diagnostics_for_config_entry,
)
from pytest_homeassistant_custom_component.typing import ClientSessionGenerator

from homeassistant.core import HomeAssistant

from .conftest import API_KEY


async def test_diagnostics_redacted(
    hass: HomeAssistant,
    hass_client: ClientSessionGenerator,
    setup_integration: MockConfigEntry,
) -> None:
    """Diagnostics include the data but never the key or Lidarr's address."""
    diagnostics = await get_diagnostics_for_config_entry(
        hass, hass_client, setup_integration
    )

    assert diagnostics["entry"]["data"]["api_key"] == "**REDACTED**"
    assert diagnostics["entry"]["data"]["url"] == "**REDACTED**"
    assert diagnostics["system_status"]["version"] == "3.1.2.4913"
    assert len(diagnostics["albums"]) == 3
    assert diagnostics["albums"][0]["lidarr_url"] == "**REDACTED**"
    # Which cached image each item uses, without a signed URL.
    assert diagnostics["albums"][0]["cover_url"] == "album/1/cover-500.jpg"
    assert diagnostics["artists"][1]["image_url"] == "artist/4/poster-500.jpg"
    assert diagnostics["artists"][4]["image_url"] is None
    assert diagnostics["coordinator"]["separate_link_url"] is False
    assert "authSig" not in json.dumps(diagnostics)

    dumped = json.dumps(diagnostics)
    assert API_KEY not in dumped
    assert "lidarr.local" not in dumped
    assert "/config" not in dumped
