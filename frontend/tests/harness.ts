// Loads the built card into a blank page with a fake `hass` object.

import { readFileSync } from "node:fs";
import type { Page } from "@playwright/test";

const BUNDLE = readFileSync(
  new URL(
    "../../custom_components/lidarr_recently_added/frontend/lidarr-recently-added-card.js",
    import.meta.url,
  ),
  "utf8",
);
const ORIGIN = "http://harness.test";
// 1x1 PNG.
const PNG = Buffer.from(
  "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
  "base64",
);

export const ALBUMS = [
  {
    artist: "Royal Blood",
    album: "Typhoons",
    added: new Date(Date.now() - 2 * 3600_000).toISOString(),
    cover_url: "/api/lidarr_recently_added/image/e/album/1/cover-500.jpg?v=1&authSig=x",
    musicbrainz_id: "a1",
    lidarr_url: "https://lidarr.example.com/album/a1",
  },
  {
    artist: "Wet Leg",
    album: "Moisturizer",
    added: new Date(Date.now() - 26 * 3600_000).toISOString(),
    cover_url: "/api/lidarr_recently_added/image/e/album/2/cover-500.jpg?v=1&authSig=x",
    musicbrainz_id: "a2",
    lidarr_url: "https://lidarr.example.com/album/a2",
  },
  {
    artist: "Nobody",
    album: "No Cover",
    added: new Date(Date.now() - 9 * 86400_000).toISOString(),
    cover_url: null,
    musicbrainz_id: "a3",
    lidarr_url: "https://lidarr.example.com/album/a3",
  },
];

export const ARTISTS = [
  {
    artist: "Royal Blood",
    added: new Date(Date.now() - 3600_000).toISOString(),
    image_url: "/api/lidarr_recently_added/image/e/artist/230/poster-500.jpg?v=1&authSig=x",
    musicbrainz_id: "r1",
    lidarr_url: "https://lidarr.example.com/artist/r1",
  },
  {
    artist: "The Last Dinner Party",
    added: new Date(Date.now() - 5 * 3600_000).toISOString(),
    image_url: null,
    musicbrainz_id: "r2",
    lidarr_url: "https://lidarr.example.com/artist/r2",
  },
  {
    artist: "Broken Image",
    added: new Date(Date.now() - 7 * 3600_000).toISOString(),
    image_url: "/api/lidarr_recently_added/image/e/artist/9/poster-500.jpg?missing",
    musicbrainz_id: "r3",
    lidarr_url: "https://lidarr.example.com/artist/r3",
  },
];

export interface MountOptions {
  config?: Record<string, unknown>;
  /** Install Music Assistant (players and the play_media service). */
  musicAssistant?: boolean;
  /** Make play_media fail with this message. */
  failWith?: string;
  extraStates?: Record<string, unknown>;
  dark?: boolean;
  width?: number;
}

export async function mount(page: Page, options: MountOptions = {}): Promise<void> {
  await page.route(`${ORIGIN}/**`, async (route) => {
    const url = new URL(route.request().url());
    if (url.pathname === "/") {
      await route.fulfill({ contentType: "text/html", body: PAGE });
    } else if (url.pathname === "/card.js") {
      await route.fulfill({ contentType: "text/javascript", body: BUNDLE });
    } else if (url.pathname.startsWith("/api/lidarr_recently_added/image/") && !url.search.includes("missing")) {
      await route.fulfill({ contentType: "image/png", body: PNG });
    } else {
      await route.fulfill({ status: 404, body: "" });
    }
  });
  await page.goto(`${ORIGIN}/`);
  await page.evaluate((opts) => (window as any).setup(opts), {
    albums: ALBUMS,
    artists: ARTISTS,
    ...options,
  });
  await page.locator("lidarr-recently-added-card").waitFor();
}

export async function calls(page: Page): Promise<any[]> {
  return page.evaluate(() => (window as any).calls);
}

export async function toasts(page: Page): Promise<string[]> {
  return page.evaluate(() => (window as any).toasts);
}

const PAGE = `<!doctype html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
  html {
    --primary-color: #03a9f4;
    --text-primary-color: #fff;
    --primary-text-color: #212121;
    --secondary-text-color: #727272;
    --card-background-color: #fff;
    --divider-color: rgba(0, 0, 0, 0.12);
    --ha-card-border-radius: 12px;
    font-family: Roboto, system-ui, sans-serif;
  }
  html.dark {
    --primary-text-color: #e1e1e1;
    --secondary-text-color: #9b9b9b;
    --card-background-color: #1c1c1c;
    --divider-color: rgba(225, 225, 225, 0.12);
    background: #111;
  }
  body { margin: 16px; background: #fafafa; }
  html.dark body { background: #111; }
  ha-card {
    display: block;
    background: var(--card-background-color);
    border-radius: var(--ha-card-border-radius);
    box-shadow: 0 1px 2px rgba(0,0,0,.15);
  }
</style>
<script type="module" src="/card.js"></script>
<script type="module">
  window.calls = [];
  window.toasts = [];
  document.addEventListener("hass-notification", (e) => window.toasts.push(e.detail.message));
  window.setup = (opts) => {
    if (opts.dark) document.documentElement.classList.add("dark");
    const players = opts.musicAssistant === false ? [] : [
      ["media_player.living_room", "Living Room", "idle"],
      ["media_player.kitchen", "Kitchen", "playing"],
    ];
    const states = {
      "sensor.lidarr_recently_added_albums": { entity_id: "sensor.lidarr_recently_added_albums", state: opts.albums[0]?.added ?? "unknown", attributes: { items: opts.albums } },
      "sensor.lidarr_recently_added_artists": { entity_id: "sensor.lidarr_recently_added_artists", state: opts.artists[0]?.added ?? "unknown", attributes: { items: opts.artists } },
      ...Object.fromEntries(players.map(([id, name, state]) => [id, { entity_id: id, state, attributes: { friendly_name: name } }])),
      ...(opts.extraStates ?? {}),
    };
    const entities = {
      "sensor.lidarr_recently_added_albums": { entity_id: "sensor.lidarr_recently_added_albums", platform: "lidarr_recently_added" },
      "sensor.lidarr_recently_added_artists": { entity_id: "sensor.lidarr_recently_added_artists", platform: "lidarr_recently_added" },
      ...Object.fromEntries(players.map(([id]) => [id, { entity_id: id, platform: "music_assistant" }])),
    };
    const hass = {
      states,
      entities,
      services: opts.musicAssistant === false ? {} : { music_assistant: { play_media: {} } },
      locale: { language: "en" },
      callService: async (domain, service, data, target, notifyOnError) => {
        window.calls.push({ domain, service, data, target, notifyOnError });
        if (opts.failWith) throw { code: "home_assistant_error", message: opts.failWith };
      },
    };
    window.hass = hass;
    const card = document.createElement("lidarr-recently-added-card");
    card.setConfig({
      type: "custom:lidarr-recently-added-card",
      albums_entity: "sensor.lidarr_recently_added_albums",
      artists_entity: "sensor.lidarr_recently_added_artists",
      ...(opts.config ?? {}),
    });
    card.hass = hass;
    const wrap = document.createElement("div");
    wrap.style.width = (opts.width ?? 600) + "px";
    wrap.appendChild(card);
    document.body.appendChild(wrap);
  };
</script>
</head>
<body></body>
</html>`;
