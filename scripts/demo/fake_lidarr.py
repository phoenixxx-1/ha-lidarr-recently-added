"""A stand-in Lidarr for demos and screenshots.

Serves the few API endpoints the integration uses, with fictional artists and
generated artwork. Image shapes match what real Lidarr returns: some artists
have public remote URLs, some have a path inside Lidarr's container as their
remoteUrl, and some have no images at all.

Usage: python fake_lidarr.py [port]
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from functools import cache
import io
import random
import sys

from aiohttp import web
from PIL import Image, ImageDraw, ImageFilter

API_KEY = "0123456789abcdef0123456789abcdef"
NOW = datetime.now(UTC)

ALBUMS = [
    # (album id, artist id, title, type, released, imported hours ago, tracks)
    (101, 1, "Afterglow Avenue", "Album", "2026-09-26", 2, 11),
    (102, 2, "Paper Satellites", "Album", "2026-10-03", 9, 10),
    (103, 3, "Saltwater Hymns", "EP", "2026-08-15", 20, 5),
    (104, 4, "Night Ferry", "Album", "2025-11-07", 30, 12),
    (105, 5, "Static Bloom", "Album", "2026-05-22", 52, 9),
    (106, 6, "Kites Over the Harbour", "Single", "2026-10-10", 75, 2),
    (107, 7, "Glass Weather", "Album", "2024-03-01", 100, 13),
    (108, 8, "Lanterns", "Album", "2026-02-14", 140, 10),
    (109, 9, "The Long Way Round (Deluxe Edition)", "Album", "2023-06-30", 200, 18),
    (110, 10, "Low Tide Radio", "EP", "2026-07-04", 260, 6),
]

ARTISTS = [
    # (artist id, name, added hours ago, image shape)
    (1, "Harbour Lights", 3, "remote"),
    (2, "Neon Orchard", 10, "local"),
    (3, "Velvet Static", 21, "local"),
    (4, "Northbound Atlas", 31, "remote"),
    (5, "The Quiet Arcade", 55, "none"),
    (6, "Kestrel Park", 80, "local"),
    (7, "Saint Ivory", 101, "local"),
    (8, "Moth Radio", 150, "remote"),
    (9, "Hollow Pines", 210, "local"),
    (10, "Marlowe & The Tides", 270, "none"),
]
ARTIST_NAMES = {artist_id: name for artist_id, name, _, _ in ARTISTS}

PALETTES = [
    ((255, 94, 98), (255, 195, 113)),
    ((32, 0, 44), (203, 180, 212)),
    ((0, 82, 212), (101, 199, 247)),
    ((17, 153, 142), (56, 239, 125)),
    ((252, 70, 107), (63, 94, 251)),
    ((15, 32, 39), (44, 83, 100)),
    ((238, 156, 167), (255, 221, 225)),
    ((255, 216, 155), (25, 84, 123)),
    ((131, 58, 180), (253, 29, 29)),
    ((67, 198, 172), (25, 22, 84)),
]


def iso(hours_ago: float) -> str:
    return (NOW - timedelta(hours=hours_ago)).strftime("%Y-%m-%dT%H:%M:%SZ")


@cache
def artwork(seed: int, round_subject: bool) -> bytes:
    """Abstract generated artwork, so no real covers are needed."""
    rng = random.Random(seed)
    size = 500
    top, bottom = PALETTES[seed % len(PALETTES)]
    image = Image.new("RGB", (size, size))
    draw = ImageDraw.Draw(image)
    for y in range(size):
        t = y / size
        draw.line(
            [(0, y), (size, y)],
            fill=tuple(int(a + (b - a) * t) for a, b in zip(top, bottom, strict=True)),
        )
    overlay = Image.new("RGBA", (size, size))
    shapes = ImageDraw.Draw(overlay)
    for _ in range(rng.randint(3, 6)):
        r = rng.randint(40, 180)
        x, y = rng.randint(0, size), rng.randint(0, size)
        colour = (*PALETTES[rng.randrange(len(PALETTES))][rng.randint(0, 1)], 110)
        if rng.random() < 0.5:
            shapes.ellipse([x - r, y - r, x + r, y + r], fill=colour)
        else:
            shapes.rectangle([x - r, y - r // 3, x + r, y + r // 3], fill=colour)
    if round_subject:
        # A soft "head and shoulders" so artist images read as portraits.
        shapes.ellipse([180, 110, 320, 250], fill=(255, 255, 255, 150))
        shapes.ellipse([120, 260, 380, 560], fill=(255, 255, 255, 120))
    overlay = overlay.filter(ImageFilter.GaussianBlur(2))
    image = Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")
    buffer = io.BytesIO()
    image.save(buffer, "JPEG", quality=85)
    return buffer.getvalue()


def album_resource(album_id: int, *, mapped: bool) -> dict:
    _, artist_id, title, album_type, released, _, tracks = next(
        a for a in ALBUMS if a[0] == album_id
    )
    remote = f"https://coverartarchive.org/release/{album_id}/front.jpg"
    return {
        "id": album_id,
        "artistId": artist_id,
        "title": title,
        "foreignAlbumId": f"00000000-0000-4000-8000-{album_id:012d}",
        "releaseDate": f"{released}T00:00:00Z",
        "albumType": album_type,
        "images": [
            {
                "url": f"/MediaCover/Albums/{album_id}/cover.jpg?lastWrite=638950000000000000"
                if mapped
                else remote,
                "coverType": "cover",
                "extension": ".jpg",
                "remoteUrl": remote,
            }
        ],
        "statistics": {
            "trackFileCount": tracks,
            "trackCount": tracks,
            "totalTrackCount": tracks,
        },
    }


def artist_resource(artist_id: int, name: str, hours_ago: float, shape: str) -> dict:
    images = []
    if shape != "none":
        for cover_type in ("poster", "fanart", "banner", "clearlogo"):
            ext = ".png" if cover_type == "clearlogo" else ".jpg"
            images.append(
                {
                    "url": f"/MediaCover/{artist_id}/{cover_type}{ext}?lastWrite=638950000000000000",
                    "coverType": cover_type,
                    "extension": ext,
                    "remoteUrl": f"https://images.lidarr.audio/{artist_id}/{cover_type}{ext}"
                    if shape == "remote"
                    else f"/config/MediaCover/{artist_id}/{cover_type}{ext}",
                }
            )
    return {
        "id": artist_id,
        "artistName": name,
        "foreignArtistId": f"00000000-0000-4000-9000-{artist_id:012d}",
        "added": iso(hours_ago),
        "images": images,
        "statistics": {"albumCount": 1 + artist_id % 4},
    }


@web.middleware
async def require_api_key(request: web.Request, handler):
    if request.path.startswith("/api/") and request.headers.get("X-Api-Key") != API_KEY:
        return web.json_response({"message": "Unauthorized"}, status=401)
    if request.path.startswith("/MediaCover/"):
        # Like Lidarr: the UI path needs a login session, not the API key.
        return web.Response(status=401)
    return await handler(request)


async def system_status(_: web.Request) -> web.Response:
    return web.json_response(
        {
            "appName": "Lidarr",
            "instanceName": "Lidarr",
            "version": "3.1.6.5078",
            "urlBase": "",
        }
    )


async def history(request: web.Request) -> web.Response:
    records = []
    record_id = 10_000
    for album_id, artist_id, _title, _type, _released, hours, tracks in ALBUMS:
        for track in range(min(tracks, 4)):
            record_id -= 1
            records.append(
                {
                    "id": record_id,
                    "albumId": album_id,
                    "artistId": artist_id,
                    "trackId": album_id * 100 + track,
                    "date": iso(hours + track / 3600),
                    "eventType": "trackFileImported",
                    "album": album_resource(album_id, mapped=False),
                    "artist": {"id": artist_id, "artistName": ARTIST_NAMES[artist_id]},
                }
            )
    page = int(request.query.get("page", 1))
    size = int(request.query.get("pageSize", 10))
    return web.json_response(
        {
            "page": page,
            "pageSize": size,
            "totalRecords": len(records),
            "records": records[(page - 1) * size : page * size],
        }
    )


async def albums(request: web.Request) -> web.Response:
    ids = [int(i) for i in request.query.getall("albumIds", [])]
    return web.json_response([album_resource(i, mapped=True) for i in ids])


async def artists(_: web.Request) -> web.Response:
    return web.json_response([artist_resource(*artist) for artist in ARTISTS])


async def media_cover(request: web.Request) -> web.Response:
    kind = request.match_info["kind"]
    item_id = int(request.match_info["item_id"])
    filename = request.match_info["filename"]
    if kind == "artist":
        shape = next((a[3] for a in ARTISTS if a[0] == item_id), "none")
        if shape == "none" or not filename.startswith(("poster", "fanart", "banner")):
            return web.Response(status=404)
        return web.Response(body=artwork(item_id + 50, True), content_type="image/jpeg")
    if kind == "album" and any(a[0] == item_id for a in ALBUMS):
        return web.Response(body=artwork(item_id, False), content_type="image/jpeg")
    return web.Response(status=404)


def main() -> None:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8686
    app = web.Application(middlewares=[require_api_key])
    app.router.add_get("/api/v1/system/status", system_status)
    app.router.add_get("/api/v1/history", history)
    app.router.add_get("/api/v1/album", albums)
    app.router.add_get("/api/v1/artist", artists)
    app.router.add_get("/api/v1/mediacover/{kind}/{item_id}/{filename}", media_cover)
    web.run_app(app, host="127.0.0.1", port=port, print=None)


if __name__ == "__main__":
    main()
