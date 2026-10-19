// custom:lidarr-recently-added-card
//
// Shows the albums and artists from the Lidarr Recently Added sensors as
// cover art. Tap plays the album (or artist) on a Music Assistant player;
// hold opens a menu.

import { LitElement, css, html, nothing, svg, type PropertyValues } from "lit";
import { repeat } from "lit/directives/repeat.js";
import {
  mdiAlbum,
  mdiOpenInNew,
  mdiPlay,
  mdiPlaylistPlay,
  mdiPlaylistPlus,
  mdiRadio,
  mdiSpeaker,
} from "@mdi/js";

import {
  MA_DOMAIN,
  errorMessage,
  friendlyName,
  initials,
  items,
  maPlayers,
  musicAssistantAvailable,
  relativeTime,
  resolvePlayer,
  type AlbumItem,
  type ArtistItem,
  type CardConfig,
  type Hass,
} from "./helpers";
import { defineWhenReady } from "./define";
import { openPopup, type PopupEntry } from "./popup";

declare const __CARD_VERSION__: string;

const CARD_TYPE = "lidarr-recently-added-card";
const INTEGRATION = "lidarr_recently_added";
const HOLD_MS = 500;
const MOVE_TOLERANCE = 10;

type Enqueue = "replace" | "next" | "add";

type Target =
  | { kind: "album"; item: AlbumItem; element: HTMLElement }
  | { kind: "artist"; item: ArtistItem; element: HTMLElement };

interface PendingHold {
  pointerId: number;
  x: number;
  y: number;
  timer: number;
  target: Target;
}

const LABELS: Record<string, string> = {
  title: "Title",
  albums_entity: "Recently added albums sensor",
  artists_entity: "Recently added artists sensor",
  layout: "Layout",
  max_items: "Maximum items",
  show_artists: "Show artists",
  show_added: "Show when added",
  player: "Music Assistant player",
  player_entity: "Player helper",
  artist_radio: "Artist tap starts radio",
  lidarr_link: "Show “Open in Lidarr” in the hold menu",
};

const HELPERS: Record<string, string> = {
  player: "Tapping a cover plays it here.",
  player_entity:
    "Optional. An input_select or text helper holding a player's entity ID or name. Takes priority over the fixed player.",
  lidarr_link:
    "Only turn on if the Lidarr address works from the devices that show this dashboard.",
};

export class LidarrRecentlyAddedCard extends LitElement {
  static override properties = {
    hass: { attribute: false },
    config: { state: true },
    now: { state: true },
    failedImages: { state: true },
  };

  hass?: Hass;
  config?: CardConfig;
  now = Date.now();
  failedImages = new Set<string>();

  private albums: AlbumItem[] = [];
  private artists: ArtistItem[] = [];
  private pendingHold?: PendingHold;
  private suppressClick = false;
  private lastMenuAt = 0;
  private ticker?: number;

  // ---- Lovelace API -------------------------------------------------------

  setConfig(config: CardConfig): void {
    if (!config.albums_entity && !config.artists_entity) {
      throw new Error("Set albums_entity, artists_entity, or both.");
    }
    if (config.layout && !["strip", "wall"].includes(config.layout)) {
      throw new Error('layout must be "strip" or "wall".');
    }
    this.config = {
      layout: "strip",
      show_artists: true,
      show_added: true,
      artist_radio: true,
      lidarr_link: false,
      ...config,
    };
  }

  getCardSize(): number {
    const albumRows = this.config?.layout === "wall" ? 8 : 4;
    return (this.config?.albums_entity ? albumRows : 0) + (this.showArtists ? 2 : 0) + 1;
  }

  getGridOptions(): Record<string, unknown> {
    return { columns: 12, min_columns: 6, rows: "auto" };
  }

  static getConfigForm(): Record<string, unknown> {
    const sensor = { entity: { filter: { integration: INTEGRATION, domain: "sensor" } } };
    return {
      schema: [
        { name: "title", selector: { text: {} } },
        { name: "albums_entity", selector: sensor },
        { name: "artists_entity", selector: sensor },
        {
          type: "grid",
          name: "",
          schema: [
            {
              name: "layout",
              selector: {
                select: {
                  mode: "dropdown",
                  options: [
                    { value: "strip", label: "Strip (one scrolling row)" },
                    { value: "wall", label: "Wall (grid)" },
                  ],
                },
              },
            },
            { name: "max_items", selector: { number: { min: 1, max: 25, mode: "box" } } },
          ],
        },
        {
          type: "grid",
          name: "",
          schema: [
            { name: "show_artists", selector: { boolean: {} } },
            { name: "show_added", selector: { boolean: {} } },
          ],
        },
        {
          type: "expandable",
          name: "",
          flatten: true,
          title: "Playback (Music Assistant)",
          schema: [
            {
              name: "player",
              selector: { entity: { filter: { integration: MA_DOMAIN, domain: "media_player" } } },
            },
            {
              name: "player_entity",
              selector: {
                entity: {
                  filter: [
                    { domain: "input_select" },
                    { domain: "select" },
                    { domain: "input_text" },
                    { domain: "text" },
                  ],
                },
              },
            },
            { name: "artist_radio", selector: { boolean: {} } },
          ],
        },
        { name: "lidarr_link", selector: { boolean: {} } },
      ],
      computeLabel: (schema: { name: string }) => LABELS[schema.name],
      computeHelper: (schema: { name: string }) => HELPERS[schema.name],
    };
  }

  static getStubConfig(hass: Hass): CardConfig {
    const find = (suffix: string): string | undefined => {
      const ids = Object.values(hass.entities ?? {})
        .filter((entry) => entry?.platform === INTEGRATION)
        .map((entry) => entry!.entity_id);
      return (ids.length ? ids : Object.keys(hass.states)).find((id) =>
        id.endsWith(suffix),
      );
    };
    const player = maPlayers(hass)[0];
    return {
      type: `custom:${CARD_TYPE}`,
      albums_entity: find("recently_added_albums") ?? "sensor.lidarr_recently_added_albums",
      artists_entity: find("recently_added_artists") ?? "sensor.lidarr_recently_added_artists",
      layout: "strip",
      ...(player ? { player } : {}),
    };
  }

  // ---- Lifecycle ----------------------------------------------------------

  override connectedCallback(): void {
    super.connectedCallback();
    // Keep "Added 2h ago" current.
    this.ticker = window.setInterval(() => {
      this.now = Date.now();
    }, 60_000);
  }

  override disconnectedCallback(): void {
    super.disconnectedCallback();
    window.clearInterval(this.ticker);
    this.cancelHold();
  }

  protected override shouldUpdate(changed: PropertyValues): boolean {
    if (!this.config) {
      return false;
    }
    if (changed.size > 1 || !changed.has("hass")) {
      return true;
    }
    const old = changed.get("hass") as Hass | undefined;
    if (!old || !this.hass) {
      return true;
    }
    // Only re-render when something this card shows has changed.
    const { albums_entity, artists_entity, player_entity, player } = this.config;
    return (
      [albums_entity, artists_entity, player_entity, player].some(
        (id) => id !== undefined && old.states[id] !== this.hass!.states[id],
      ) ||
      old.entities !== this.hass.entities ||
      old.services !== this.hass.services ||
      old.locale !== this.hass.locale
    );
  }

  // ---- Rendering ----------------------------------------------------------

  private get showArtists(): boolean {
    return Boolean(this.config?.show_artists && this.config.artists_entity);
  }

  private get language(): string {
    return this.hass?.locale?.language ?? this.hass?.language ?? navigator.language;
  }

  protected override render() {
    if (!this.config || !this.hass) {
      return nothing;
    }
    const config = this.config;
    const canPlay = musicAssistantAvailable(this.hass);
    this.albums = items<AlbumItem>(this.hass, config.albums_entity, config.max_items) ?? [];
    this.artists = this.showArtists
      ? (items<ArtistItem>(this.hass, config.artists_entity, config.max_items) ?? [])
      : [];
    const both = Boolean(config.albums_entity) && this.showArtists;

    return html`
      <ha-card>
        ${config.title ? html`<h1 class="card-header">${config.title}</h1>` : nothing}
        <div
          class="content ${config.title ? "" : "no-title"} ${canPlay ? "can-play" : ""}"
          @pointerdown=${this.onPointerDown}
          @pointermove=${this.onPointerMove}
          @pointerup=${this.cancelHold}
          @pointercancel=${this.cancelHold}
          @click=${this.onClick}
          @contextmenu=${this.onContextMenu}
          @keydown=${this.onKeyDown}
        >
          ${config.albums_entity
            ? this.renderSection(
                config.albums_entity,
                both ? "Albums" : undefined,
                this.albums.length
                  ? html`<div class="albums ${config.layout}">
                      ${repeat(
                        this.albums,
                        (item, index) => item.musicbrainz_id ?? `${item.artist}|${item.album}|${index}`,
                        (item, index) => this.renderAlbum(item, index, canPlay),
                      )}
                    </div>`
                  : html`<div class="empty">No albums imported yet.</div>`,
              )
            : nothing}
          ${this.showArtists
            ? this.renderSection(
                config.artists_entity!,
                both ? "Artists" : undefined,
                this.artists.length
                  ? html`<div class="artists">
                      ${repeat(
                        this.artists,
                        (item, index) => item.musicbrainz_id ?? `${item.artist}|${index}`,
                        (item, index) => this.renderArtist(item, index, canPlay),
                      )}
                    </div>`
                  : html`<div class="empty">No artists added yet.</div>`,
              )
            : nothing}
        </div>
      </ha-card>
    `;
  }

  private renderSection(entityId: string, label: string | undefined, body: unknown) {
    const state = this.hass!.states[entityId];
    let content = body;
    if (!state) {
      content = html`<div class="warning">Entity not found: ${entityId}</div>`;
    } else if (state.state === "unavailable") {
      content = html`<div class="empty">Lidarr is unavailable.</div>`;
    }
    return html`
      <section>
        ${label ? html`<h2 class="section-label">${label}</h2>` : nothing}
        ${content}
      </section>
    `;
  }

  private renderAlbum(item: AlbumItem, index: number, canPlay: boolean) {
    const title = item.album ?? "Unknown album";
    const artist = item.artist ?? "";
    const hint = canPlay ? "Tap to play, hold for options" : "";
    return html`
      <button
        class="tile album"
        data-kind="album"
        data-index=${index}
        aria-label=${[title, artist && `by ${artist}`, hint].filter(Boolean).join(", ")}
        aria-haspopup="menu"
      >
        <div class="cover">
          ${this.renderImage(item.cover_url, html`<svg viewBox="0 0 24 24" aria-hidden="true">
            ${svg`<path d=${mdiAlbum}></path>`}
          </svg>`)}
          ${canPlay
            ? html`<span class="play" aria-hidden="true"
                ><svg viewBox="0 0 24 24">${svg`<path d=${mdiPlay}></path>`}</svg
              ></span>`
            : nothing}
        </div>
        <div class="title">${title}</div>
        ${artist ? html`<div class="subtitle">${artist}</div>` : nothing}
        ${this.config!.show_added && item.added
          ? html`<div class="added">Added ${relativeTime(item.added, this.language, this.now)}</div>`
          : nothing}
      </button>
    `;
  }

  private renderArtist(item: ArtistItem, index: number, canPlay: boolean) {
    const name = item.artist ?? "Unknown artist";
    const hint = canPlay ? "Tap to play, hold for options" : "";
    return html`
      <button
        class="tile artist"
        data-kind="artist"
        data-index=${index}
        aria-label=${[name, hint].filter(Boolean).join(", ")}
        aria-haspopup="menu"
      >
        <div class="avatar">
          ${this.renderImage(item.image_url, html`<span class="initials">${initials(item.artist)}</span>`)}
        </div>
        <div class="name">${name}</div>
        ${this.config!.show_added && item.added
          ? html`<div class="added">${relativeTime(item.added, this.language, this.now)}</div>`
          : nothing}
      </button>
    `;
  }

  private renderImage(url: string | null | undefined, fallback: unknown) {
    if (!url || this.failedImages.has(url)) {
      return html`<div class="placeholder">${fallback}</div>`;
    }
    return html`<img
      src=${url}
      alt=""
      loading="lazy"
      decoding="async"
      draggable="false"
      @error=${() => {
        this.failedImages = new Set(this.failedImages).add(url);
      }}
    />`;
  }

  // ---- Interaction --------------------------------------------------------

  private targetFrom(event: Event): Target | undefined {
    const element = (event.target as HTMLElement | null)?.closest<HTMLElement>(".tile");
    if (!element) {
      return undefined;
    }
    const index = Number(element.dataset.index);
    if (element.dataset.kind === "album" && this.albums[index]) {
      return { kind: "album", item: this.albums[index], element };
    }
    if (element.dataset.kind === "artist" && this.artists[index]) {
      return { kind: "artist", item: this.artists[index], element };
    }
    return undefined;
  }

  private onPointerDown = (event: PointerEvent): void => {
    if (event.button !== 0) {
      return;
    }
    const target = this.targetFrom(event);
    if (!target) {
      return;
    }
    this.cancelHold();
    this.suppressClick = false;
    this.pendingHold = {
      pointerId: event.pointerId,
      x: event.clientX,
      y: event.clientY,
      target,
      timer: window.setTimeout(() => {
        const pending = this.pendingHold;
        this.pendingHold = undefined;
        if (pending) {
          this.suppressClick = true;
          this.openMenu(pending.target, pending.x, pending.y);
        }
      }, HOLD_MS),
    };
  };

  private onPointerMove = (event: PointerEvent): void => {
    const pending = this.pendingHold;
    if (
      pending &&
      event.pointerId === pending.pointerId &&
      Math.hypot(event.clientX - pending.x, event.clientY - pending.y) > MOVE_TOLERANCE
    ) {
      this.cancelHold();
    }
  };

  private cancelHold = (): void => {
    if (this.pendingHold) {
      window.clearTimeout(this.pendingHold.timer);
      this.pendingHold = undefined;
    }
  };

  private onClick = (event: MouseEvent): void => {
    const target = this.targetFrom(event);
    if (!target) {
      return;
    }
    if (this.suppressClick) {
      // The pointer was held: the menu is already open.
      this.suppressClick = false;
      return;
    }
    const rect = target.element.getBoundingClientRect();
    this.tap(target, event.clientX || rect.left + rect.width / 2, event.clientY || rect.top + rect.height / 2);
  };

  private onContextMenu = (event: MouseEvent): void => {
    const target = this.targetFrom(event);
    if (!target) {
      return;
    }
    event.preventDefault();
    this.cancelHold();
    // Touch browsers send contextmenu on long press too; don't open twice.
    if (Date.now() - this.lastMenuAt > 800) {
      this.suppressClick = true;
      this.openMenu(target, event.clientX, event.clientY);
    }
  };

  private onKeyDown = (event: KeyboardEvent): void => {
    if (event.key === "ContextMenu" || (event.key === "F10" && event.shiftKey)) {
      const target = this.targetFrom(event);
      if (target) {
        event.preventDefault();
        const rect = target.element.getBoundingClientRect();
        this.openMenu(target, rect.left + rect.width / 2, rect.top + rect.height / 2);
      }
    }
  };

  private tap(target: Target, x: number, y: number): void {
    if (!this.hass || !musicAssistantAvailable(this.hass) || !this.mediaName(target)) {
      return;
    }
    const player = resolvePlayer(this.hass, this.config!);
    if (player) {
      void this.play(target, player, "replace");
    } else {
      this.choosePlayer(target, x, y);
    }
  }

  private mediaName(target: Target): string | undefined {
    return (target.kind === "album" ? target.item.album : target.item.artist) ?? undefined;
  }

  private openMenu(target: Target, x: number, y: number): void {
    const hass = this.hass;
    if (!hass) {
      return;
    }
    const entries: PopupEntry[] = [];
    const name = this.mediaName(target);
    if (musicAssistantAvailable(hass) && name) {
      const player = resolvePlayer(hass, this.config!);
      const play = (enqueue: Enqueue) => () =>
        player ? void this.play(target, player, enqueue) : this.choosePlayer(target, x, y, enqueue);
      const radio = target.kind === "artist" && this.config!.artist_radio;
      entries.push(
        {
          label: radio ? "Start radio" : "Play now",
          icon: radio ? mdiRadio : mdiPlay,
          secondary: player ? `on ${friendlyName(hass, player)}` : undefined,
          action: play("replace"),
        },
        { label: "Play next", icon: mdiPlaylistPlay, action: play("next") },
        { label: "Add to queue", icon: mdiPlaylistPlus, action: play("add") },
        {
          label: "Choose player…",
          icon: mdiSpeaker,
          action: () => this.choosePlayer(target, x, y),
        },
      );
    }
    const link = target.item.lidarr_url;
    if (this.config!.lidarr_link && link) {
      entries.push({
        label: "Open in Lidarr",
        icon: mdiOpenInNew,
        action: () => window.open(link, "_blank", "noopener"),
      });
    }
    if (!entries.length) {
      return;
    }
    this.lastMenuAt = Date.now();
    openPopup({
      heading: name ?? "",
      subheading: target.kind === "album" ? (target.item.artist ?? undefined) : "Artist",
      entries,
      x,
      y,
      returnFocus: target.element,
    });
  }

  private choosePlayer(target: Target, x: number, y: number, enqueue: Enqueue = "replace"): void {
    const hass = this.hass!;
    const players = maPlayers(hass);
    if (!players.length) {
      this.toast("No Music Assistant players found.");
      return;
    }
    const current = resolvePlayer(hass, this.config!);
    this.lastMenuAt = Date.now();
    openPopup({
      heading: "Play on…",
      subheading: this.mediaName(target),
      entries: players.map((id) => ({
        label: friendlyName(hass, id),
        secondary: stateLabel(hass.states[id]?.state),
        icon: mdiSpeaker,
        checked: id === current,
        action: () => void this.play(target, id, enqueue),
      })),
      x,
      y,
      returnFocus: target.element,
    });
  }

  private async play(target: Target, player: string, enqueue: Enqueue): Promise<void> {
    const hass = this.hass!;
    const name = this.mediaName(target)!;
    const radio = target.kind === "artist" && this.config!.artist_radio;
    const data: Record<string, unknown> =
      target.kind === "album"
        ? { media_id: name, media_type: "album", enqueue }
        : { media_id: name, media_type: "artist", enqueue };
    if (target.kind === "album" && target.item.artist) {
      data.artist = target.item.artist;
    }
    if (radio) {
      data.radio_mode = true;
    }
    const where = friendlyName(hass, player);
    try {
      await hass.callService(MA_DOMAIN, "play_media", data, { entity_id: player }, false);
      const what = radio ? `${name} radio` : name;
      this.toast(
        enqueue === "next"
          ? `${what} will play next on ${where}`
          : enqueue === "add"
            ? `Added ${what} to the queue on ${where}`
            : `Playing ${what} on ${where}`,
      );
    } catch (err) {
      this.toast(`Couldn't play ${name} on ${where}: ${errorMessage(err)}`);
    }
  }

  private toast(message: string): void {
    this.dispatchEvent(
      new CustomEvent("hass-notification", {
        detail: { message },
        bubbles: true,
        composed: true,
      }),
    );
  }

  // ---- Styles -------------------------------------------------------------

  static override styles = css`
    :host {
      --lra-cover-size: 132px;
      --lra-wall-min: 96px;
      --lra-avatar-size: 72px;
      --lra-radius: 10px;
      --lra-gap: 12px;
      --lra-tint: color-mix(
        in srgb,
        var(--primary-color) 16%,
        var(--card-background-color, var(--ha-card-background, #fff))
      );
    }
    ha-card {
      height: 100%;
      overflow: hidden;
    }
    .card-header {
      margin: 0;
      padding: 16px 16px 0;
      font-family: inherit;
      font-size: var(--ha-card-header-font-size, 20px);
      font-weight: var(--ha-font-weight-normal, 400);
      line-height: 1.3;
      color: var(--ha-card-header-color, var(--primary-text-color));
    }
    .content {
      display: flex;
      flex-direction: column;
      gap: 16px;
      padding: 12px 0 16px;
    }
    .content.no-title {
      padding-top: 16px;
    }
    section {
      min-width: 0;
    }
    .section-label {
      margin: 0 16px 8px;
      font-size: 13px;
      font-weight: var(--ha-font-weight-medium, 500);
      letter-spacing: 0.02em;
      color: var(--secondary-text-color);
    }
    .empty,
    .warning {
      margin: 0 16px;
      font-size: 14px;
      color: var(--secondary-text-color);
    }
    .warning {
      color: var(--warning-color, #ff9800);
    }

    /* Rows that scroll sideways, snapping to whole items. */
    .albums.strip,
    .artists {
      display: flex;
      gap: var(--lra-gap);
      overflow-x: auto;
      overscroll-behavior-x: contain;
      scroll-snap-type: x mandatory;
      scroll-padding-inline: 16px;
      padding: 0 16px 4px;
      scrollbar-width: thin;
      scrollbar-color: var(--divider-color, rgba(127, 127, 127, 0.3)) transparent;
    }
    .albums.strip .tile {
      flex: none;
      width: var(--lra-cover-size);
    }
    .albums.wall {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(var(--lra-wall-min), 1fr));
      gap: 16px var(--lra-gap);
      padding: 0 16px;
    }

    .tile {
      display: flex;
      flex-direction: column;
      min-width: 0;
      margin: 0;
      padding: 0;
      border: 0;
      background: none;
      color: inherit;
      font: inherit;
      text-align: start;
      scroll-snap-align: start;
      -webkit-tap-highlight-color: transparent;
      -webkit-touch-callout: none;
      user-select: none;
      -webkit-user-select: none;
      touch-action: manipulation;
      cursor: default;
    }
    .can-play .tile {
      cursor: pointer;
    }
    .tile:focus-visible {
      outline: none;
    }
    .tile:focus-visible .cover,
    .tile:focus-visible .avatar {
      outline: 2px solid var(--primary-color);
      outline-offset: 2px;
    }

    .cover {
      position: relative;
      width: 100%;
      aspect-ratio: 1;
      border-radius: var(--lra-radius);
      overflow: hidden;
      background: var(--lra-tint);
      transition: transform 150ms ease-out;
    }
    .can-play .tile:active .cover,
    .can-play .tile:active .avatar {
      transform: scale(0.97);
    }
    img {
      display: block;
      width: 100%;
      height: 100%;
      object-fit: cover;
      -webkit-user-drag: none;
    }
    .placeholder {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 100%;
      height: 100%;
      background: var(--lra-tint);
      color: var(--primary-color);
    }
    .placeholder svg {
      width: 42%;
      height: 42%;
      fill: currentColor;
      opacity: 0.55;
    }
    .play {
      position: absolute;
      right: 8px;
      bottom: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      width: 36px;
      height: 36px;
      border-radius: 50%;
      background: var(--primary-color);
      color: var(--text-primary-color, #fff);
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
      opacity: 0;
      transform: translateY(4px);
      transition:
        opacity 150ms ease-out,
        transform 150ms ease-out;
      pointer-events: none;
    }
    .play svg {
      width: 22px;
      height: 22px;
      fill: currentColor;
    }
    @media (hover: hover) {
      .tile:hover .play,
      .tile:focus-visible .play {
        opacity: 1;
        transform: none;
      }
    }

    .title,
    .name {
      margin-top: 8px;
      font-size: 14px;
      font-weight: var(--ha-font-weight-medium, 500);
      line-height: 1.3;
      color: var(--primary-text-color);
      display: -webkit-box;
      -webkit-box-orient: vertical;
      -webkit-line-clamp: 2;
      line-clamp: 2;
      overflow: hidden;
      overflow-wrap: anywhere;
    }
    .subtitle {
      margin-top: 2px;
      font-size: 13px;
      line-height: 1.3;
      color: var(--secondary-text-color);
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    .added {
      margin-top: 2px;
      font-size: 12px;
      line-height: 1.3;
      color: var(--secondary-text-color);
      opacity: 0.8;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .artist {
      flex: none;
      align-items: center;
      width: calc(var(--lra-avatar-size) + 16px);
      text-align: center;
    }
    .avatar {
      width: var(--lra-avatar-size);
      height: var(--lra-avatar-size);
      border-radius: 50%;
      overflow: hidden;
      background: var(--lra-tint);
      transition: transform 150ms ease-out;
    }
    .artist .name {
      font-size: 13px;
      text-align: center;
    }
    .initials {
      font-size: calc(var(--lra-avatar-size) * 0.36);
      font-weight: var(--ha-font-weight-medium, 500);
      letter-spacing: 0.02em;
      color: var(--primary-color);
    }

    @media (prefers-reduced-motion: reduce) {
      .cover,
      .avatar,
      .play {
        transition: none;
      }
    }
  `;
}

function stateLabel(state: string | undefined): string | undefined {
  if (!state) {
    return undefined;
  }
  return state.charAt(0).toUpperCase() + state.slice(1).replace(/_/g, " ");
}

defineWhenReady(CARD_TYPE, LidarrRecentlyAddedCard);

interface CustomCardEntry {
  type: string;
  name: string;
  description: string;
  preview?: boolean;
  documentationURL?: string;
}
const registry = window as unknown as { customCards?: CustomCardEntry[] };
registry.customCards ??= [];
if (!registry.customCards.some((card) => card.type === CARD_TYPE)) {
  registry.customCards.push({
    type: CARD_TYPE,
    name: "Lidarr Recently Added",
    description: "Cover art for recently added albums and artists, with tap to play.",
    preview: true,
    documentationURL: "https://github.com/phoenixxx-1/ha-lidarr-recently-added",
  });
}

console.info(`%c LIDARR-RECENTLY-ADDED-CARD %c ${__CARD_VERSION__} `, "font-weight:600", "");
