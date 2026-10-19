"""Constants for the Lidarr Recently Added integration."""

from __future__ import annotations

import logging
from typing import Final

DOMAIN: Final = "lidarr_recently_added"
LOGGER = logging.getLogger(__package__)

DEFAULT_NAME: Final = "Lidarr"
MANUFACTURER: Final = "Lidarr"

CONF_MAX_ITEMS: Final = "max_items"
CONF_SCAN_INTERVAL: Final = "scan_interval"
CONF_ALBUMS_ENABLED: Final = "albums_enabled"
CONF_ARTISTS_ENABLED: Final = "artists_enabled"

DEFAULT_VERIFY_SSL: Final = True
DEFAULT_MAX_ITEMS: Final = 10
MIN_MAX_ITEMS: Final = 1
MAX_MAX_ITEMS: Final = 25

# Scan interval is configured in minutes.
DEFAULT_SCAN_INTERVAL: Final = 30
MIN_SCAN_INTERVAL: Final = 5
MAX_SCAN_INTERVAL: Final = 1440

EVENT_NEW_ALBUM: Final = "lidarr_recently_added_album"
EVENT_NEW_ARTIST: Final = "lidarr_recently_added_artist"

ATTR_ITEMS: Final = "items"

# EntityHistoryEventType values in Lidarr (src/NzbDrone.Core/History/EntityHistory.cs).
# The API filter takes the integer value; responses carry the camelCase name.
HISTORY_EVENT_TRACK_FILE_IMPORTED: Final = 3
HISTORY_EVENT_DOWNLOAD_IMPORTED: Final = 8
HISTORY_IMPORT_EVENT_TYPES: Final = (
    HISTORY_EVENT_TRACK_FILE_IMPORTED,
    HISTORY_EVENT_DOWNLOAD_IMPORTED,
)

# Track imports produce one history record per track, so a page holds roughly
# a dozen albums. Stop after a bounded number of pages so a library with lots
# of upgrades can't turn one refresh into an unbounded crawl.
HISTORY_PAGE_SIZE: Final = 250
HISTORY_MAX_PAGES: Final = 8

REQUEST_TIMEOUT: Final = 60
