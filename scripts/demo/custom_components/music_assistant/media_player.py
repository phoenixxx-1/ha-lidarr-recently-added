"""Demo players."""

from __future__ import annotations

from homeassistant.components.media_player import MediaPlayerEntity, MediaPlayerState
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback


async def async_setup_platform(
    hass: HomeAssistant,
    config,
    async_add_entities: AddEntitiesCallback,
    discovery_info=None,
) -> None:
    async_add_entities(
        [
            DemoPlayer("living_room", "Living Room", MediaPlayerState.IDLE),
            DemoPlayer("kitchen", "Kitchen", MediaPlayerState.PLAYING),
            DemoPlayer("office", "Office", MediaPlayerState.OFF),
        ]
    )


class DemoPlayer(MediaPlayerEntity):
    def __init__(self, key: str, name: str, state: MediaPlayerState) -> None:
        self._attr_unique_id = f"demo_ma_{key}"
        self._attr_name = name
        self._attr_state = state
        self.entity_id = f"media_player.{key}"
