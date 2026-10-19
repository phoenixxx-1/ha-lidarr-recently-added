# Lidarr Recently Added

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://hacs.xyz/docs/faq/custom_repositories)
[![Validate](https://github.com/phoenixxx-1/ha-lidarr-recently-added/actions/workflows/validate.yml/badge.svg)](https://github.com/phoenixxx-1/ha-lidarr-recently-added/actions/workflows/validate.yml)
[![Tests](https://github.com/phoenixxx-1/ha-lidarr-recently-added/actions/workflows/tests.yml/badge.svg)](https://github.com/phoenixxx-1/ha-lidarr-recently-added/actions/workflows/tests.yml)

A Home Assistant integration that shows the albums and artists most recently
added to your [Lidarr](https://lidarr.audio/) library, with cover art. It
includes a dashboard card that plays an album in Music Assistant when you tap
its cover, and it fires an event when a new album or artist arrives, so you
can be notified without polling.

<p>
  <img src="https://raw.githubusercontent.com/phoenixxx-1/ha-lidarr-recently-added/main/docs/screenshots/strip-desktop-light.webp" alt="The card on a dashboard: a row of album covers and a row of artist avatars" width="640">
  <img src="https://raw.githubusercontent.com/phoenixxx-1/ha-lidarr-recently-added/main/docs/screenshots/strip-phone-dark.webp" alt="The same card on a phone in dark mode" width="180">
</p>

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
| Dashboard card with tap to play (Music Assistant) | — | ✅ |

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

### Advanced configuration

Most people won't need this. Under **Configure → Advanced** there is one
optional field:

| Option | Description |
|---|---|
| Lidarr web address for links | The address used for the `lidarr_url` links in sensors and events. Leave it empty to use the connection URL. |

You only need it if Home Assistant connects to Lidarr on a different address
from the one you open in your browser, for example an internal IP address
when your browser uses a reverse-proxy name that Home Assistant can't
resolve. Home Assistant never connects to this address; it is only checked
to be a valid URL. The usual fix is to give Home Assistant the same address
you use in your browser, and leave this empty.

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
> [dashboard card](#dashboard-card) below.

### `sensor.lidarr_recently_added_albums`

- **State:** when the newest album was imported (a timestamp).
- **`items` attribute:** the newest albums, newest first.

| Field | Example | Notes |
|---|---|---|
| `artist` | `Radiohead` | |
| `album` | `In Rainbows` | |
| `release_date` | `2007-10-10` | |
| `added` | `2026-10-18T20:00:03+00:00` | Latest import time for the album. |
| `cover_url` | `/api/lidarr_recently_added/image/…` | Album cover served by Home Assistant (see [Images](#images)), or `null`. |
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
| `image_url` | `/api/lidarr_recently_added/image/…` | Artist image served by Home Assistant, or `null` if Lidarr has none. |
| `album_count` | `9` | From Lidarr's artist statistics. |
| `musicbrainz_id` | `…` | MusicBrainz artist ID. |
| `lidarr_url` | `http://…/artist/<id>` | Opens the artist in Lidarr. |

The `items` attribute is excluded from the recorder, so it doesn't fill your
database.

### `sensor.lidarr_latest_album` and `sensor.lidarr_latest_artist`

- **State:** `Artist – Album` for the newest album, or the newest artist's
  name. `unknown` when there is nothing yet.
- **Picture:** the album cover or artist image, when Lidarr has one.
- **Attributes:** the same fields as one entry of `items` above.

### Where the data comes from

- **Albums** come from Lidarr's history, filtered to import events. Lidarr
  records one event per imported track, so events are grouped per album and
  the newest import time is kept. A quality upgrade counts as a new import,
  so an upgraded album moves back to the top. Music that Lidarr found on disk
  rather than downloaded has no import event and won't appear.
- **Artists** come from your library, sorted by the date they were added.

### Images

Artwork comes from Lidarr's own image cache, through Home Assistant:

- `cover_url`, `image_url` and the sensor pictures point at Home Assistant
  (`/api/lidarr_recently_added/image/…`), not at Lidarr or a third-party site.
- Home Assistant fetches the image from Lidarr using the API key, and passes
  the picture on. Your API key never leaves Home Assistant.
- The links are signed, so a dashboard, notification or `<img>` tag can load
  them without logging in. A link only works for that one image and expires
  after a week; the sensors renew them automatically. Restarting Home
  Assistant also renews them.
- Because every image comes from Home Assistant itself, they load over HTTPS
  when your dashboard does, and work without internet access.
- Artists use their poster, then fanart, then banner. Logos are skipped,
  because a transparent wordmark looks wrong in a round avatar. Albums use
  their cover, then the disc image.
- An item only has no image when Lidarr has none at all.

Why not use the image addresses in Lidarr's API directly? Since Lidarr
2.14.1, when an artist's metadata has no images Lidarr rebuilds the list from
its local cache. Those entries carry a file path inside Lidarr as their
"remote" URL (for example `/config/MediaCover/230/poster.jpg`), which a
browser can't load. That can be most of the artists in a library. Lidarr's own
web interface always loads images from its cache, and so does this
integration.

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
  "cover_url": "/api/lidarr_recently_added/image/…/album/1234/cover-500.jpg?v=…&authSig=…",
  "album_type": "Album",
  "track_count": 10,
  "musicbrainz_id": "…",
  "lidarr_url": "http://192.168.1.10:8686/album/…",
  "config_entry_id": "…"
}
```

To watch events, open **Developer tools → Events** and listen for
`lidarr_recently_added_album`.

## Dashboard card

The integration includes a card, `custom:lidarr-recently-added-card`. There is
nothing extra to install: Home Assistant loads it on every dashboard once the
integration is set up, and it always matches the integration's version.

<p>
  <img src="https://raw.githubusercontent.com/phoenixxx-1/ha-lidarr-recently-added/main/docs/screenshots/wall-desktop-dark.webp" alt="Wall layout: a grid of album covers filling the width" width="640">
  <img src="https://raw.githubusercontent.com/phoenixxx-1/ha-lidarr-recently-added/main/docs/screenshots/menu-phone-dark.webp" alt="Holding a cover opens a menu: Play now, Play next, Add to queue, Choose player" width="180">
</p>

### Adding it

Edit a dashboard, choose **Add card**, and search for **Lidarr Recently
Added**. The card has a visual editor. In YAML:

```yaml
type: custom:lidarr-recently-added-card
albums_entity: sensor.lidarr_recently_added_albums
artists_entity: sensor.lidarr_recently_added_artists
layout: strip
player: media_player.living_room
```

| Option | Default | Description |
|---|---|---|
| `albums_entity` | | The **Recently added albums** sensor. |
| `artists_entity` | | The **Recently added artists** sensor. Set at least one of the two. |
| `title` | none | Optional heading. |
| `layout` | `strip` | `strip`: one row that scrolls sideways, good for a narrow column. `wall`: a grid that fills the card's width. |
| `max_items` | all | Show at most this many albums and artists. The sensors' **Number of items** option sets the upper limit. |
| `show_artists` | `true` | Show the row of artist avatars. |
| `show_added` | `true` | Show when each item was added, for example "Added 2h ago". |
| `player` | none | The Music Assistant player to play on. |
| `player_entity` | none | A helper (`input_select`, `select`, `input_text` or `text`) holding the player's entity ID or name. Takes priority over `player`, so other controls can choose the player. |
| `artist_radio` | `true` | Tapping an artist starts radio based on them, rather than playing their albums. |
| `lidarr_link` | `false` | Add **Open in Lidarr** to the hold menu. See below. |

The card sizes itself in sections views. Covers use your theme's colours and
fonts, in light and dark mode. If you use card-mod, these variables adjust the
sizes: `--lra-cover-size` (strip covers, 132px), `--lra-wall-min` (smallest
wall tile, 96px), `--lra-avatar-size` (72px), `--lra-radius` (10px).

### Playing music

Playback uses [Music Assistant](https://www.home-assistant.io/integrations/music_assistant/).

- **Tap** a cover to play the album on your player, replacing what's playing.
  A message confirms it: "Playing Typhoons on Living Room".
- **Hold** a cover (or right-click it, or press the context-menu key) for more:
  **Play now**, **Play next**, **Add to queue** and **Choose player…**.
- **Tap an artist** to start radio based on that artist, or to play their
  music if `artist_radio` is `false`.

Which player is used:

1. If `player_entity` is set and names a player, that player.
2. Otherwise `player`.
3. If neither is set, the card asks each time, listing your Music Assistant
   players.

Albums are played by name: the card asks Music Assistant for the album title
by that artist. The album needs to be in Music Assistant's library, which
usually means its library scan has run since Lidarr imported the files. If
Music Assistant can't find it, the card shows the reason, for example "No
playable items found", instead of failing silently.

Without Music Assistant, tapping does nothing and the hold menu has no play
options.

<p>
  <img src="https://raw.githubusercontent.com/phoenixxx-1/ha-lidarr-recently-added/main/docs/screenshots/picker-phone-light.webp" alt="With no player set, tapping asks which Music Assistant player to use" width="180">
  <img src="https://raw.githubusercontent.com/phoenixxx-1/ha-lidarr-recently-added/main/docs/screenshots/toast-error-desktop-light.webp" alt="Messages after playing an album, and when Music Assistant can't find one" width="640">
</p>

### Open in Lidarr

The card doesn't link to Lidarr by default: the address Home Assistant uses is
often an internal one that won't open on, say, a wall tablet, or leads to
Lidarr's login page. Set `lidarr_link: true` to add **Open in Lidarr** to the
hold menu when the link works from the devices that show your dashboard. If
your browser reaches Lidarr on a different address from Home Assistant, set
that address under [Advanced configuration](#advanced-configuration).

### Without the card

The sensors work with any card. This markdown card lists the latest albums
using only built-in cards:

```yaml
type: markdown
title: Recently added albums
content: |-
  {% set items = state_attr('sensor.lidarr_recently_added_albums', 'items') or [] %}
  {% if items %}
  | | Album | Added |
  |:-:|---|---|
  {%- for a in items %}
  | {% if a.cover_url %}<img src="{{ a.cover_url }}" width="56" height="56">{% endif %} | **{{ a.album }}**<br>{{ a.artist }}{% if a.release_date %} · {{ a.release_date[:4] }}{% endif %} | {{ (a.added | as_datetime | relative_time) }} ago |
  {%- endfor %}
  {% else %}
  Nothing imported yet.
  {% endif %}
```

Keep `content: |-` as written: `>` or `>-` joins the lines and breaks the
table.

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

`image` and `url` are understood by the Home Assistant Companion apps, which
load relative image paths from your Home Assistant. Other notify services
ignore them.

## Troubleshooting

- **"Failed to connect":** check the URL opens Lidarr in a browser from the
  machine running Home Assistant, including the base path if you use one.
- **"Not Lidarr":** the address points at another application (for example
  Readarr or Prowlarr). Check the port.
- **No cover art:** the item has no image in Lidarr either. Check the artist
  or album in Lidarr; refreshing the artist there usually fetches artwork.
  Diagnostics list which cached image each item uses.
- **Card shows "Custom element doesn't exist":** check the integration is set
  up and loaded, then reload the page. After an update, a hard refresh (or
  clearing the app's cache in the Companion app) makes sure the new card
  loads.
- **Tapping a cover does nothing:** Music Assistant isn't set up, or the card
  can't find any Music Assistant players.
- **Diagnostics:** on the integration's page, open the menu (⋮) and choose
  **Download diagnostics**. The API key and addresses are redacted.

## Not affiliated with Lidarr

This is an independent community project. It is not affiliated with,
endorsed by, or supported by the Lidarr project. Please report problems
[here](https://github.com/phoenixxx-1/ha-lidarr-recently-added/issues), not
to Lidarr.

## License

[MIT](LICENSE)
