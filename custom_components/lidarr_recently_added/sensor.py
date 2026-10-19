"""Sensors for recently added Lidarr albums and artists."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.const import ATTR_ENTITY_PICTURE, CONF_URL
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .api import normalize_url
from .const import ATTR_ITEMS, DOMAIN, MANUFACTURER
from .coordinator import (
    AlbumItem,
    ArtistItem,
    LidarrRecentlyAddedConfigEntry,
    LidarrRecentlyAddedCoordinator,
    RecentlyAddedData,
)

PARALLEL_UPDATES = 0


type RecentItem = AlbumItem | ArtistItem

# Home Assistant rejects states longer than 255 characters.
MAX_STATE_LENGTH = 255


def _latest_title(items: Sequence[RecentItem]) -> str | None:
    """Return the newest item's title, truncated to a valid state."""
    if not items or (title := items[0].title) is None:
        return None
    if len(title) > MAX_STATE_LENGTH:
        return title[: MAX_STATE_LENGTH - 1] + "…"
    return title


@dataclass(frozen=True, kw_only=True)
class LidarrRecentlyAddedSensorDescription(SensorEntityDescription):
    """Describes a recently added sensor."""

    items_fn: Callable[[RecentlyAddedData], Sequence[RecentItem] | None]
    enabled_fn: Callable[[LidarrRecentlyAddedCoordinator], bool]
    value_fn: Callable[[Sequence[RecentItem]], datetime | str | None]
    # True: expose the whole list as `items`. False: expose the newest item's fields.
    list_attributes: bool


SENSORS: tuple[LidarrRecentlyAddedSensorDescription, ...] = (
    LidarrRecentlyAddedSensorDescription(
        key="recently_added_albums",
        translation_key="recently_added_albums",
        device_class=SensorDeviceClass.TIMESTAMP,
        items_fn=lambda data: data.albums,
        enabled_fn=lambda coordinator: coordinator.albums_enabled,
        value_fn=lambda items: items[0].added if items else None,
        list_attributes=True,
    ),
    LidarrRecentlyAddedSensorDescription(
        key="recently_added_artists",
        translation_key="recently_added_artists",
        device_class=SensorDeviceClass.TIMESTAMP,
        items_fn=lambda data: data.artists,
        enabled_fn=lambda coordinator: coordinator.artists_enabled,
        value_fn=lambda items: items[0].added if items else None,
        list_attributes=True,
    ),
    LidarrRecentlyAddedSensorDescription(
        key="latest_album",
        translation_key="latest_album",
        items_fn=lambda data: data.albums,
        enabled_fn=lambda coordinator: coordinator.albums_enabled,
        value_fn=_latest_title,
        list_attributes=False,
    ),
    LidarrRecentlyAddedSensorDescription(
        key="latest_artist",
        translation_key="latest_artist",
        items_fn=lambda data: data.artists,
        enabled_fn=lambda coordinator: coordinator.artists_enabled,
        value_fn=_latest_title,
        list_attributes=False,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: LidarrRecentlyAddedConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the sensors from a config entry."""
    coordinator = entry.runtime_data.coordinator
    registry = er.async_get(hass)
    entities: list[LidarrRecentlyAddedSensor] = []
    for description in SENSORS:
        if description.enabled_fn(coordinator):
            entities.append(LidarrRecentlyAddedSensor(coordinator, description))
        elif entity_id := registry.async_get_entity_id(
            "sensor", DOMAIN, f"{entry.entry_id}_{description.key}"
        ):
            # Turned off in the options flow: remove it rather than leave an
            # orphaned "unavailable" entity behind.
            registry.async_remove(entity_id)
    async_add_entities(entities)


class LidarrRecentlyAddedSensor(
    CoordinatorEntity[LidarrRecentlyAddedCoordinator], SensorEntity
):
    """A sensor describing the newest albums or artists."""

    _attr_has_entity_name = True
    # The list can exceed the recorder's 16 KB attribute limit, and its
    # history has no value. Image URLs carry a signature that expires, so
    # there is no point storing them either.
    _unrecorded_attributes = frozenset(
        {ATTR_ITEMS, ATTR_ENTITY_PICTURE, "cover_url", "image_url"}
    )
    entity_description: LidarrRecentlyAddedSensorDescription

    def __init__(
        self,
        coordinator: LidarrRecentlyAddedCoordinator,
        description: LidarrRecentlyAddedSensorDescription,
    ) -> None:
        """Initialise the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        entry = coordinator.config_entry
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer=MANUFACTURER,
            sw_version=entry.runtime_data.system_status.get("version"),
            entry_type=DeviceEntryType.SERVICE,
            configuration_url=normalize_url(entry.data[CONF_URL]),
        )

    @property
    def _items(self) -> Sequence[RecentItem]:
        return self.entity_description.items_fn(self.coordinator.data) or ()

    @property
    def native_value(self) -> datetime | str | None:
        """Return the newest item's timestamp or title."""
        return self.entity_description.value_fn(self._items)

    @property
    def entity_picture(self) -> str | None:
        """Show the newest item's cover or image in place of the icon."""
        items = self._items
        return self.coordinator.image_url(items[0].image) if items else None

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return the newest items, or the newest item's fields."""
        items = self._items
        image_url = self.coordinator.image_url
        if self.entity_description.list_attributes:
            return {ATTR_ITEMS: [item.as_dict(image_url) for item in items]}
        return items[0].as_dict(image_url) if items else None
