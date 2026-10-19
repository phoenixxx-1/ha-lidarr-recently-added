# Lidarr Recently Added

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://hacs.xyz/docs/faq/custom_repositories)
[![Validate](https://github.com/phoenixxx-1/ha-lidarr-recently-added/actions/workflows/validate.yml/badge.svg)](https://github.com/phoenixxx-1/ha-lidarr-recently-added/actions/workflows/validate.yml)
[![Tests](https://github.com/phoenixxx-1/ha-lidarr-recently-added/actions/workflows/tests.yml/badge.svg)](https://github.com/phoenixxx-1/ha-lidarr-recently-added/actions/workflows/tests.yml)

A Home Assistant integration that shows the albums and artists most recently
added to your [Lidarr](https://lidarr.audio/) library, with cover art, so you
can put them on a dashboard. It also fires an event when a new album or artist
arrives, so you can be notified without polling.

## How it differs from the core Lidarr integration

The built-in [Lidarr integration](https://www.home-assistant.io/integrations/lidarr)
reports disk space, the download queue, wanted albums and an album count. It
has no list of recently added music, no cover art and no events.

This integration fills that gap and is designed to run alongside it. It uses
its own domain (`lidarr_recently_added`), adds no Python dependencies, and does
not touch the core integration's configuration.

| | Core `lidarr` | Lidarr Recently Added |
|---|---|---|
| Disk space, queue, wanted | ✅ | — |
| Recently added albums, with covers | — | ✅ |
| Recently added artists, with images | — | ✅ |
| Events for new albums and artists | — | ✅ |

## Installation

Requires Home Assistant 2026.3 or newer.

### HACS (custom repository)

[![Open your Home Assistant instance and open this repository in HACS.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=phoenixxx-1&repository=ha-lidarr-recently-added&category=integration)

Or add it by hand:

1. In HACS, open the menu (⋮) in the top right and choose **Custom repositories**.
2. Enter `https://github.com/phoenixxx-1/ha-lidarr-recently-added` and pick
   the **Integration** type.
3. Search for **Lidarr Recently Added**, download it, and restart Home Assistant.

### Manual

Copy `custom_components/lidarr_recently_added` into the `custom_components`
folder of your Home Assistant configuration and restart.

## Configuration

[![Open your Home Assistant instance and start setting up the integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=lidarr_recently_added)

Go to **Settings → Devices & services → Add integration** and search for
**Lidarr Recently Added**.

| Field | Description |
|---|---|
| URL | The address you use to open Lidarr, including any base path, e.g. `http://192.168.1.10:8686` or `https://example.com/lidarr`. |
| API key | In Lidarr under **Settings → General → Security**. |
| Verify SSL certificate | Turn off only for a self-signed certificate. |

Each Lidarr instance can be added once. If Lidarr later rejects the API key,
Home Assistant asks you to re-authenticate.

### Options

Open the integration and choose **Configure**:

| Option | Default | Description |
|---|---|---|
| Number of items | 10 | How many albums and artists each sensor lists (1–25). |
| Update interval | 30 min | How often Lidarr is asked for new items (5–1440 minutes). |
| Recently added albums sensor | On | Turning it off removes the sensor and stops its API calls and events. |
| Recently added artists sensor | On | As above, for artists. |

## Sensors

Each Lidarr instance gets one device with four sensors. Entity IDs follow the
device name, which is Lidarr's instance name (usually `Lidarr`).

| Sensor | State | Picture | Attributes |
|---|---|---|---|
| `sensor.lidarr_latest_album` | `Artist – Album` of the newest import | Its cover | That album's fields |
| `sensor.lidarr_latest_artist` | Name of the newest artist | Their image | That artist's fields |
| `sensor.lidarr_recently_added_albums` | When the newest album was imported | Newest cover | `items`: the list |
| `sensor.lidarr_recently_added_artists` | When the newest artist was added | Newest image | `items`: the list |

Use the **Latest** sensors for a quick look or a simple dashboard tile, and
the **Recently added** sensors for lists and for automations that react to
the timestamp.

> **Where's the list?** Home Assistant's device page shows each sensor's
> state, not its attributes. To see the full list, select **Recently added
> albums** (or artists) and expand **Attributes** in the dialog that opens.
> The list is meant for dashboard cards; see the
> [examples](#dashboard-examples) below.

### `sensor.lidarr_recently_added_albums`

- **State:** when the newest album was imported (a timestamp).
- **`items` attribute:** the newest albums, newest first.

| Field | Example | Notes |
|---|---|---|
| `artist` | `Radiohead` | |
| `album` | `In Rainbows` | |
| `release_date` | `2007-10-10` | |
| `added` | `2026-10-18T20:00:03+00:00` | Latest import time for the album. |
| `cover_url` | `https://coverartarchive.org/…` | Public URL, or `null` if Lidarr has none. |
| `album_type` | `Album` | `Album`, `EP`, `Single`, … |
| `track_count` | `10` | Tracks on the selected release. |
| `musicbrainz_id` | `…` | MusicBrainz release group ID. |
| `lidarr_url` | `http://…/album/<id>` | Opens the album in Lidarr. |

### `sensor.lidarr_recently_added_artists`

- **State:** when the newest artist was added (a timestamp).
- **`items` attribute:** the most recently added artists, newest first.

| Field | Example | Notes |
|---|---|---|
| `artist` | `Radiohead` | |
| `added` | `2026-10-18T12:00:00+00:00` | |
| `image_url` | `https://assets.fanart.tv/…` | Public URL, or `null`. |
| `album_count` | `9` | From Lidarr's artist statistics. |
| `musicbrainz_id` | `…` | MusicBrainz artist ID. |
| `lidarr_url` | `http://…/artist/<id>` | Opens the artist in Lidarr. |

The `items` attribute is excluded from the recorder, so it doesn't fill your
database.

### `sensor.lidarr_latest_album` and `sensor.lidarr_latest_artist`

- **State:** `Artist – Album` for the newest album, or the newest artist's
  name. `unknown` when there is nothing yet.
- **Picture:** the album cover or artist image, when Lidarr has a public one.
- **Attributes:** the same fields as one entry of `items` above.

### Where the data comes from

- **Albums** come from Lidarr's history, filtered to import events. Lidarr
  records one event per imported track, so events are grouped per album and
  the newest import time is kept. A quality upgrade counts as a new import,
  so an upgraded album moves back to the top. Music that Lidarr found on disk
  rather than downloaded has no import event and won't appear.
- **Artists** come from your library, sorted by the date they were added.

### Images and privacy

Your API key is never placed in an attribute, event or URL. Lidarr's own
`/MediaCover` images need a login, so this integration only uses the public
image addresses Lidarr stores (Cover Art Archive, fanart.tv and similar). Your
browser loads those images directly from those sites, including the sensor
pictures shown in place of icons. Items without a public image have an empty
image field, and their sensors show the normal icon.

## Events

When a refresh finds an album or artist that wasn't in the previous list, an
event is fired with the same fields as the `items` entry plus
`config_entry_id`. Nothing fires for the first refresh after Home Assistant
starts or the integration reloads, so restarts don't announce the whole list.
If Lidarr is unreachable for a while, items imported in the meantime are
announced once it's back.

| Event | Fired for |
|---|---|
| `lidarr_recently_added_album` | A new album in the albums list |
| `lidarr_recently_added_artist` | A new artist in the artists list |

Example `lidarr_recently_added_album` payload:

```json
{
  "artist": "Radiohead",
  "album": "In Rainbows",
  "release_date": "2007-10-10",
  "added": "2026-10-18T20:00:03+00:00",
  "cover_url": "https://coverartarchive.org/release/…/front.jpg",
  "album_type": "Album",
  "track_count": 10,
  "musicbrainz_id": "…",
  "lidarr_url": "http://192.168.1.10:8686/album/…",
  "config_entry_id": "…"
}
```

To watch events, open **Developer tools → Events** and listen for
`lidarr_recently_added_album`.

## Dashboard examples

For a quick start, add the device's sensors to a dashboard with **Add to
dashboard** on the device page. The Latest sensors show the newest album and
artist with their pictures. For a full list, use the examples below.

Both examples use only built-in cards. Change the entity ID if your device
isn't called `Lidarr`.

### List of the latest albums

```yaml
type: markdown
title: Recently added albums
content: |-
  {% set items = state_attr('sensor.lidarr_recently_added_albums', 'items') or [] %}
  {% if items %}
  | | Album | Added |
  |:-:|---|---|
  {%- for a in items %}
  | {% if a.cover_url %}<img src="{{ a.cover_url }}" width="56" height="56">{% endif %} | **[{{ a.album }}]({{ a.lidarr_url }})**<br>{{ a.artist }}{% if a.release_date %} · {{ a.release_date[:4] }}{% endif %} | {{ (a.added | as_datetime | relative_time) }} ago |
  {%- endfor %}
  {% else %}
  Nothing imported yet.
  {% endif %}
```

### Grid of cover tiles

Change `columns` to fit your dashboard.

```yaml
type: markdown
title: New in the library
content: |-
  {% set columns = 4 %}
  {% set items = state_attr('sensor.lidarr_recently_added_albums', 'items') or [] %}
  {% if items %}
  |{% for _ in range(columns) %} |{% endfor %}
  |{% for _ in range(columns) %}:-:|{% endfor %}
  {%- for row in items | batch(columns, '') %}
  |{% for a in row %}{% if a %}{% if a.cover_url %}[<img src="{{ a.cover_url }}" width="110" height="110">]({{ a.lidarr_url }}){% endif %}<br>**{{ a.album }}**<br>{{ a.artist }}{% endif %} |{% endfor %}
  {%- endfor %}
  {% else %}
  Nothing imported yet.
  {% endif %}
```

For artists, use `sensor.lidarr_recently_added_artists` with `image_url` in
place of `cover_url` and `artist` in place of `album`.

## Example automation: notify on a new album

```yaml
alias: Notify when a new album arrives
triggers:
  - trigger: event
    event_type: lidarr_recently_added_album
actions:
  - action: notify.notify
    data:
      title: New album in Lidarr
      message: "{{ trigger.event.data.artist }} – {{ trigger.event.data.album }}"
      data:
        image: "{{ trigger.event.data.cover_url }}"
        url: "{{ trigger.event.data.lidarr_url }}"
mode: queued
```

`image` and `url` are understood by the Home Assistant Companion apps. Other
notify services ignore them.

## Troubleshooting

- **"Failed to connect":** check the URL opens Lidarr in a browser from the
  machine running Home Assistant, including the base path if you use one.
- **"Not Lidarr":** the address points at another application (for example
  Readarr or Prowlarr). Check the port.
- **No cover art:** Lidarr only has a public image for some releases. Items
  without one show an empty `cover_url`.
- **Diagnostics:** on the integration's page, open the menu (⋮) and choose
  **Download diagnostics**. The API key and addresses are redacted.

## Not affiliated with Lidarr

This is an independent community project. It is not affiliated with,
endorsed by, or supported by the Lidarr project. Please report problems
[here](https://github.com/phoenixxx-1/ha-lidarr-recently-added/issues), not
to Lidarr.

## License

[MIT](LICENSE)
