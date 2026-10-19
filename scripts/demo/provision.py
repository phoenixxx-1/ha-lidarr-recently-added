"""Prepare a fresh Home Assistant for the card demo.

Completes onboarding, adds the integration through its config flow (against
fake_lidarr.py), saves a demo dashboard, and writes the access tokens to a
JSON file for the screenshot script.

Usage: python provision.py http://127.0.0.1:8123 tokens.json
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
import sys

import aiohttp
from fake_lidarr import API_KEY

LIDARR_URL = "http://127.0.0.1:8686"

DASHBOARD_PATH = "music-demo"
CARD = "custom:lidarr-recently-added-card"
ALBUMS = "sensor.lidarr_recently_added_albums"
ARTISTS = "sensor.lidarr_recently_added_artists"

DASHBOARD = {
    "title": "Home",
    "views": [
        {
            "title": "Music",
            "path": "music",
            "type": "sections",
            "max_columns": 2,
            "sections": [
                {
                    "type": "grid",
                    "cards": [
                        {"type": "heading", "heading": "New in the library"},
                        {
                            "type": CARD,
                            "albums_entity": ALBUMS,
                            "artists_entity": ARTISTS,
                            "layout": "strip",
                            "player": "media_player.living_room",
                            "lidarr_link": True,
                        },
                    ],
                },
                {
                    "type": "grid",
                    "cards": [
                        {"type": "heading", "heading": "Latest"},
                        {
                            "type": "tile",
                            "entity": "sensor.lidarr_latest_album",
                            "show_entity_picture": True,
                        },
                        {
                            "type": "tile",
                            "entity": "sensor.lidarr_latest_artist",
                            "show_entity_picture": True,
                        },
                    ],
                },
            ],
        },
        {
            "title": "Wall",
            "path": "wall",
            "type": "panel",
            "cards": [
                {
                    "type": CARD,
                    "title": "Recently added",
                    "albums_entity": ALBUMS,
                    "artists_entity": ARTISTS,
                    "layout": "wall",
                    "show_artists": False,
                    "player": "media_player.living_room",
                }
            ],
        },
        {
            "title": "Ask",
            "path": "ask",
            "type": "sections",
            "sections": [
                {
                    "type": "grid",
                    "cards": [
                        {
                            "type": CARD,
                            "albums_entity": ALBUMS,
                            "artists_entity": ARTISTS,
                            "max_items": 6,
                        }
                    ],
                }
            ],
        },
    ],
}


async def wait_for(session: aiohttp.ClientSession, url: str) -> None:
    for _ in range(240):
        try:
            async with session.get(f"{url}/api/onboarding") as response:
                if response.status in (200, 401):
                    return
        except aiohttp.ClientError:
            pass
        await asyncio.sleep(1)
    raise RuntimeError("Home Assistant didn't start")


async def main(base: str, out: Path) -> None:
    client_id = f"{base}/"
    async with aiohttp.ClientSession() as session:
        await wait_for(session, base)

        async with session.post(
            f"{base}/api/onboarding/users",
            json={
                "client_id": client_id,
                "name": "Demo",
                "username": "demo",
                "password": "demo-password-123",
                "language": "en",
            },
        ) as response:
            response.raise_for_status()
            auth_code = (await response.json())["auth_code"]

        async with session.post(
            f"{base}/auth/token",
            data={
                "grant_type": "authorization_code",
                "code": auth_code,
                "client_id": client_id,
            },
        ) as response:
            response.raise_for_status()
            tokens = await response.json()
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}

        for step, payload in (
            ("core_config", {}),
            ("analytics", {}),
            (
                "integration",
                {"client_id": client_id, "redirect_uri": f"{base}/?auth_callback=1"},
            ),
        ):
            async with session.post(
                f"{base}/api/onboarding/{step}", json=payload, headers=headers
            ) as response:
                response.raise_for_status()

        async with session.post(
            f"{base}/api/config/config_entries/flow",
            json={"handler": "lidarr_recently_added"},
            headers=headers,
        ) as response:
            response.raise_for_status()
            flow = await response.json()
        async with session.post(
            f"{base}/api/config/config_entries/flow/{flow['flow_id']}",
            json={"url": LIDARR_URL, "api_key": API_KEY, "verify_ssl": True},
            headers=headers,
        ) as response:
            response.raise_for_status()
            result = await response.json()
            assert result["type"] == "create_entry", result

        async with session.ws_connect(f"{base}/api/websocket") as ws:
            await ws.receive_json()
            await ws.send_json({"type": "auth", "access_token": tokens["access_token"]})
            assert (await ws.receive_json())["type"] == "auth_ok"
            # Home Assistant 2026.10's default dashboard is the new Overview,
            # so the demo gets a dashboard of its own.
            await ws.send_json(
                {
                    "id": 1,
                    "type": "lovelace/dashboards/create",
                    "url_path": DASHBOARD_PATH,
                    "title": "Music",
                    "icon": "mdi:music",
                    "mode": "storage",
                    "show_in_sidebar": True,
                    "require_admin": False,
                }
            )
            reply = await ws.receive_json()
            assert reply["success"], reply
            await ws.send_json(
                {
                    "id": 2,
                    "type": "lovelace/config/save",
                    "url_path": DASHBOARD_PATH,
                    "config": DASHBOARD,
                }
            )
            reply = await ws.receive_json()
            assert reply["success"], reply

    out.write_text(
        json.dumps(
            {
                "access_token": tokens["access_token"],
                "refresh_token": tokens["refresh_token"],
                "expires_in": tokens["expires_in"],
                "token_type": "Bearer",
                "hassUrl": base,
                "clientId": client_id,
            }
        )
    )
    print(f"Provisioned {base}; tokens in {out}")


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1].rstrip("/"), Path(sys.argv[2])))
