# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/).

## [0.2.0] - Unreleased

First public release. Version 0.1.0 was a development build and was never
released.

### Added

- Config flow with URL (including base path), API key and SSL verification,
  validated against Lidarr's `system/status`.
- Reauthentication when Lidarr rejects the API key.
- Options for the number of items (1–25), update interval, and which sensors
  to create.
- `Recently added albums` sensor, built from Lidarr's import history and
  grouped per album.
- `Recently added artists` sensor, sorted by the date the artist was added.
- `Latest album` and `Latest artist` sensors showing the newest item's title
  and picture, so the device page is readable at a glance.
- The newest cover or artist image as the picture of each sensor.
- `lidarr_recently_added_album` and `lidarr_recently_added_artist` events for
  new items.
- Diagnostics with the API key and addresses redacted.

[0.2.0]: https://github.com/phoenixxx-1/ha-lidarr-recently-added/releases/tag/v0.2.0
