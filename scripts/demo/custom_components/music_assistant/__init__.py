"""Demo stand-in for Music Assistant: two players and play_media.

Only for screenshots and manual testing of the Lidarr Recently Added card.
It records every play request in hass.data["music_assistant_calls"] and
fails for one album so the card's error message can be seen.
"""

from __future__ import annotations

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.discovery import async_load_platform
from homeassistant.helpers.typing import ConfigType

DOMAIN = "music_assistant"
FAILING_ALBUM = "Lanterns"


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    calls: list[dict] = hass.data.setdefault("music_assistant_calls", [])

    async def play_media(call: ServiceCall) -> None:
        calls.append({"data": dict(call.data)})
        if call.data.get("media_id") == FAILING_ALBUM:
            raise HomeAssistantError(
                f"No playable items found for {FAILING_ALBUM} in your library"
            )

    hass.services.async_register(DOMAIN, "play_media", play_media)
    hass.async_create_task(
        async_load_platform(hass, Platform.MEDIA_PLAYER, DOMAIN, {}, config)
    )
    return True
