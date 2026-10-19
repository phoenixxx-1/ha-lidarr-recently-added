import { expect, test, type Locator, type Page } from "@playwright/test";

import { ALBUMS, calls, mount, toasts } from "./harness";

const card = (page: Page) => page.locator("lidarr-recently-added-card");
const albums = (page: Page) => card(page).locator(".tile.album");
const artists = (page: Page) => card(page).locator(".tile.artist");
const menu = (page: Page) => page.locator("lidarr-recently-added-popup");

async function hold(page: Page, target: Locator): Promise<void> {
  const box = (await target.boundingBox())!;
  await page.mouse.move(box.x + box.width / 2, box.y + box.width / 2);
  await page.mouse.down();
  await page.waitForTimeout(650);
  await page.mouse.up();
}

test.describe("rendering", () => {
  test("albums show cover, title, artist and when added", async ({ page }) => {
    await mount(page, { config: { player: "media_player.living_room" } });
    await expect(albums(page)).toHaveCount(3);

    const first = albums(page).first();
    await expect(first.locator(".title")).toHaveText("Typhoons");
    await expect(first.locator(".subtitle")).toHaveText("Royal Blood");
    await expect(first.locator(".added")).toHaveText(/^Added 2\s?h(r\.?)? ago$/);
    const img = first.locator("img");
    await expect(img).toHaveAttribute("src", ALBUMS[0].cover_url!);
    await expect(img).toHaveAttribute("loading", "lazy");
  });

  test("an album without a cover gets a placeholder, not a blank", async ({ page }) => {
    await mount(page);
    const third = albums(page).nth(2);
    await expect(third.locator("img")).toHaveCount(0);
    await expect(third.locator(".placeholder svg")).toBeVisible();
  });

  test("artists without an image, or with a broken one, show initials", async ({ page }) => {
    await mount(page);
    await expect(artists(page)).toHaveCount(3);
    await expect(artists(page).nth(0).locator("img")).toBeVisible();
    await expect(artists(page).nth(1).locator(".initials")).toHaveText("LD");
    // The image request fails, so the card falls back to initials.
    await expect(artists(page).nth(2).locator(".initials")).toHaveText("BI");
  });

  test("strip scrolls sideways with snap points", async ({ page }) => {
    await mount(page, { config: { layout: "strip" } });
    const strip = card(page).locator(".albums.strip");
    await expect(strip).toHaveCSS("overflow-x", "auto");
    await expect(strip).toHaveCSS("scroll-snap-type", "x mandatory");
  });

  test("wall is a grid with only real items", async ({ page }) => {
    await mount(page, { config: { layout: "wall" }, width: 900 });
    const wall = card(page).locator(".albums.wall");
    await expect(wall).toHaveCSS("display", "grid");
    await expect(wall.locator(":scope > *")).toHaveCount(3);
  });

  test("max_items and show options", async ({ page }) => {
    await mount(page, { config: { max_items: 2, show_artists: false, show_added: false } });
    await expect(albums(page)).toHaveCount(2);
    await expect(artists(page)).toHaveCount(0);
    await expect(card(page).locator(".added")).toHaveCount(0);
  });

  test("no links to Lidarr in the card", async ({ page }) => {
    await mount(page, { config: { lidarr_link: true } });
    await expect(card(page).locator("a")).toHaveCount(0);
  });

  test("a missing entity shows a warning", async ({ page }) => {
    await mount(page, { config: { albums_entity: "sensor.nope" } });
    await expect(card(page).locator(".warning")).toHaveText("Entity not found: sensor.nope");
  });

  test("setConfig rejects a config with no entities", async ({ page }) => {
    await mount(page);
    const error = await page.evaluate(() => {
      try {
        (document.createElement("lidarr-recently-added-card") as any).setConfig({ type: "x" });
        return "";
      } catch (err) {
        return (err as Error).message;
      }
    });
    expect(error).toContain("albums_entity");
  });

  test("Lovelace API: grid options, stub config, config form", async ({ page }) => {
    await mount(page);
    const result = await page.evaluate(() => {
      const ctor = customElements.get("lidarr-recently-added-card") as any;
      const card = document.querySelector("lidarr-recently-added-card") as any;
      return {
        grid: card.getGridOptions(),
        stub: ctor.getStubConfig((window as any).hass),
        form: ctor.getConfigForm().schema.length,
        registered: (window as any).customCards.some((c: any) => c.type === "lidarr-recently-added-card"),
      };
    });
    expect(result.grid).toEqual({ columns: 12, min_columns: 6, rows: "auto" });
    expect(result.stub).toEqual({
      type: "custom:lidarr-recently-added-card",
      albums_entity: "sensor.lidarr_recently_added_albums",
      artists_entity: "sensor.lidarr_recently_added_artists",
      layout: "strip",
      player: "media_player.kitchen",
    });
    expect(result.form).toBeGreaterThan(4);
    expect(result.registered).toBe(true);
  });
});

test.describe("playing", () => {
  test("tap plays the album on the fixed player", async ({ page }) => {
    await mount(page, { config: { player: "media_player.living_room" } });
    await albums(page).first().click();
    await expect.poll(() => calls(page)).toHaveLength(1);
    expect((await calls(page))[0]).toEqual({
      domain: "music_assistant",
      service: "play_media",
      data: { media_id: "Typhoons", media_type: "album", enqueue: "replace", artist: "Royal Blood" },
      target: { entity_id: "media_player.living_room" },
      notifyOnError: false,
    });
    await expect.poll(() => toasts(page)).toEqual(["Playing Typhoons on Living Room"]);
  });

  test("a player helper takes priority, by entity ID or by name", async ({ page }) => {
    await mount(page, {
      config: { player: "media_player.living_room", player_entity: "input_select.player" },
      extraStates: {
        "input_select.player": { entity_id: "input_select.player", state: "Kitchen", attributes: {} },
      },
    });
    await albums(page).first().click();
    await expect.poll(async () => (await calls(page))[0]?.target).toEqual({
      entity_id: "media_player.kitchen",
    });
  });

  test("with no player configured, tap asks which player", async ({ page }) => {
    await mount(page);
    await albums(page).nth(1).click();
    await expect(menu(page)).toBeVisible();
    await expect(menu(page).locator(".title")).toHaveText("Play on…");
    await menu(page).getByRole("menuitemradio", { name: /Kitchen/ }).click();
    await expect(menu(page)).toHaveCount(0);
    await expect.poll(async () => (await calls(page))[0]?.target).toEqual({
      entity_id: "media_player.kitchen",
    });
    await expect.poll(() => toasts(page)).toEqual(["Playing Moisturizer on Kitchen"]);
  });

  test("artist tap starts radio, unless turned off", async ({ page }) => {
    await mount(page, { config: { player: "media_player.living_room" } });
    await artists(page).first().click();
    await expect.poll(async () => (await calls(page))[0]?.data).toEqual({
      media_id: "Royal Blood",
      media_type: "artist",
      enqueue: "replace",
      radio_mode: true,
    });
    await expect.poll(() => toasts(page)).toEqual(["Playing Royal Blood radio on Living Room"]);
  });

  test("artist tap without radio", async ({ page }) => {
    await mount(page, { config: { player: "media_player.living_room", artist_radio: false } });
    await artists(page).first().click();
    await expect.poll(async () => (await calls(page))[0]?.data).toEqual({
      media_id: "Royal Blood",
      media_type: "artist",
      enqueue: "replace",
    });
  });

  test("a failed play shows the error", async ({ page }) => {
    await mount(page, {
      config: { player: "media_player.living_room" },
      failWith: "No playable items found",
    });
    await albums(page).first().click();
    await expect
      .poll(() => toasts(page))
      .toEqual(["Couldn't play Typhoons on Living Room: No playable items found"]);
  });

  test("without Music Assistant, tap does nothing", async ({ page }) => {
    await mount(page, { musicAssistant: false, config: { player: "media_player.living_room" } });
    await albums(page).first().click();
    await page.waitForTimeout(200);
    expect(await calls(page)).toEqual([]);
    await expect(menu(page)).toHaveCount(0);
    await expect(albums(page).first().locator(".play")).toHaveCount(0);
  });
});

test.describe("hold menu", () => {
  test("hold opens the menu instead of playing", async ({ page }) => {
    await mount(page, { config: { player: "media_player.living_room" } });
    await hold(page, albums(page).first());
    await expect(menu(page)).toBeVisible();
    expect(await calls(page)).toEqual([]);
    const items = menu(page).getByRole("menuitem");
    await expect(items).toHaveText([
      /Play now\s*on Living Room/,
      "Play next",
      "Add to queue",
      "Choose player…",
    ]);
  });

  test("Play next and Add to queue", async ({ page }) => {
    await mount(page, { config: { player: "media_player.living_room" } });
    await hold(page, albums(page).first());
    await menu(page).getByRole("menuitem", { name: "Play next" }).click();
    await hold(page, albums(page).nth(1));
    await menu(page).getByRole("menuitem", { name: "Add to queue" }).click();
    await expect.poll(async () => (await calls(page)).map((c) => c.data.enqueue)).toEqual(["next", "add"]);
    await expect
      .poll(() => toasts(page))
      .toEqual(["Typhoons will play next on Living Room", "Added Moisturizer to the queue on Living Room"]);
  });

  test("Choose player plays on the chosen one", async ({ page }) => {
    await mount(page, { config: { player: "media_player.living_room" } });
    await hold(page, albums(page).first());
    await menu(page).getByRole("menuitem", { name: "Choose player…" }).click();
    const kitchen = menu(page).getByRole("menuitemradio", { name: /Kitchen/ });
    await expect(menu(page).getByRole("menuitemradio", { name: /Living Room/ })).toHaveAttribute(
      "aria-checked",
      "true",
    );
    await kitchen.click();
    await expect.poll(async () => (await calls(page))[0]?.target).toEqual({
      entity_id: "media_player.kitchen",
    });
  });

  test("Open in Lidarr only when enabled", async ({ page }) => {
    await mount(page, { config: { player: "media_player.living_room", lidarr_link: true } });
    await page
      .context()
      .route("https://lidarr.example.com/**", (route) => route.fulfill({ body: "Lidarr" }));
    await hold(page, albums(page).first());
    const popupPromise = page.waitForEvent("popup");
    await menu(page).getByRole("menuitem", { name: "Open in Lidarr" }).click();
    const popup = await popupPromise;
    expect(popup.url()).toBe("https://lidarr.example.com/album/a1");
  });

  test("no Open in Lidarr by default", async ({ page }) => {
    await mount(page, { config: { player: "media_player.living_room" } });
    await hold(page, albums(page).first());
    await expect(menu(page).getByRole("menuitem", { name: "Open in Lidarr" })).toHaveCount(0);
  });

  test("without Music Assistant the menu has no play options", async ({ page }) => {
    await mount(page, { musicAssistant: false, config: { lidarr_link: true } });
    await hold(page, albums(page).first());
    await expect(menu(page).getByRole("menuitem")).toHaveText(["Open in Lidarr"]);
  });

  test("right-click opens the menu; Escape closes it and restores focus", async ({ page }) => {
    await mount(page, { config: { player: "media_player.living_room" } });
    await albums(page).first().click({ button: "right" });
    await expect(menu(page)).toBeVisible();
    await page.keyboard.press("Escape");
    await expect(menu(page)).toHaveCount(0);
    await expect(albums(page).first()).toBeFocused();
    expect(await calls(page)).toEqual([]);
  });

  test("keyboard: Enter plays, the context-menu key opens the menu", async ({ page }) => {
    await mount(page, { config: { player: "media_player.living_room" } });
    await albums(page).first().focus();
    await page.keyboard.press("Enter");
    await expect.poll(() => calls(page)).toHaveLength(1);
    await page.keyboard.press("Shift+F10");
    await expect(menu(page)).toBeVisible();
    await page.keyboard.press("ArrowDown");
    await page.keyboard.press("Enter");
    await expect.poll(async () => (await calls(page)).at(-1)?.data.enqueue).toBe("next");
  });

  test("scrolling the strip doesn't open the menu", async ({ page }) => {
    await mount(page, { config: { player: "media_player.living_room" } });
    const box = (await albums(page).first().boundingBox())!;
    await page.mouse.move(box.x + 50, box.y + 50);
    await page.mouse.down();
    await page.mouse.move(box.x + 10, box.y + 50, { steps: 5 });
    await page.waitForTimeout(650);
    await page.mouse.up();
    await expect(menu(page)).toHaveCount(0);
  });
});

test.describe("player names", () => {
  const MOVE = "media_player.sonos_move";
  const MOVE_2 = "media_player.sonos_move_2";

  test("a sync group leader is labelled with its members", async ({ page }) => {
    const group = { group_members: [MOVE, MOVE_2] };
    await mount(page, {
      players: [
        [MOVE, "Sonos Move", "playing", group],
        [MOVE_2, "Sonos Move 2", "playing", group],
        ["media_player.kitchen", "Kitchen", "idle"],
      ],
    });
    await albums(page).first().click();
    const items = menu(page).getByRole("menuitemradio");
    await expect(items).toHaveText([
      /^\s*Kitchen\s*Idle\s*$/,
      /^\s*Sonos Move \+ Move 2\s*Playing\s*$/,
      /^\s*Sonos Move 2\s*Playing · grouped with Sonos Move\s*$/,
    ]);
    await items.nth(1).click();
    await expect.poll(async () => (await calls(page))[0]?.target).toEqual({ entity_id: MOVE });
    await expect.poll(() => toasts(page)).toEqual(["Playing Typhoons on Sonos Move + Move 2"]);
  });

  test("the hold menu names the group too", async ({ page }) => {
    const group = { group_members: [MOVE, MOVE_2] };
    await mount(page, {
      config: { player: MOVE },
      players: [
        [MOVE, "Sonos Move", "playing", group],
        [MOVE_2, "Sonos Move 2", "playing", group],
      ],
    });
    await hold(page, albums(page).first());
    await expect(menu(page).getByRole("menuitem").first()).toHaveText(
      /Play now\s*on Sonos Move \+ Move 2/,
    );
  });

  test("players with the same name show their entity IDs", async ({ page }) => {
    await mount(page, {
      players: [
        [MOVE, "Sonos Move", "idle"],
        ["media_player.sonos_move_airplay", "Sonos Move", "idle"],
        ["media_player.kitchen", "Kitchen", "idle"],
      ],
    });
    await albums(page).first().click();
    await expect(menu(page).getByRole("menuitemradio")).toHaveText([
      /^\s*Kitchen\s*Idle\s*$/,
      /^\s*Sonos Move\s*Idle · media_player\.sonos_move\s*$/,
      /^\s*Sonos Move\s*Idle · media_player\.sonos_move_airplay\s*$/,
    ]);
  });

  test("players from other integrations aren't listed", async ({ page }) => {
    await mount(page, {
      players: [[MOVE, "Sonos Move", "idle"]],
      // The core Sonos entity for the same speaker: same name, not Music Assistant.
      otherPlayers: {
        "media_player.sonos_move_core": {
          entity_id: "media_player.sonos_move_core",
          state: "idle",
          attributes: { friendly_name: "Sonos Move" },
        },
      },
    });
    await albums(page).first().click();
    await expect(menu(page).getByRole("menuitemradio")).toHaveText([/^\s*Sonos Move\s*Idle\s*$/]);
  });
});
