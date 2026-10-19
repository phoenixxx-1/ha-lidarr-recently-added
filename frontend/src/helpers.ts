// Types and pure helpers shared by the card and its popups.

export interface HassEntity {
  entity_id: string;
  state: string;
  attributes: Record<string, unknown>;
}

export interface HassEntityRegistryEntry {
  entity_id: string;
  platform?: string;
}

export interface Hass {
  states: Record<string, HassEntity | undefined>;
  entities?: Record<string, HassEntityRegistryEntry | undefined>;
  services?: Record<string, Record<string, unknown> | undefined>;
  locale?: { language?: string };
  language?: string;
  callService(
    domain: string,
    service: string,
    serviceData?: Record<string, unknown>,
    target?: Record<string, unknown>,
    notifyOnError?: boolean,
  ): Promise<unknown>;
}

export interface CardConfig {
  type: string;
  title?: string;
  albums_entity?: string;
  artists_entity?: string;
  layout?: "strip" | "wall";
  max_items?: number;
  show_artists?: boolean;
  show_added?: boolean;
  player?: string;
  player_entity?: string;
  artist_radio?: boolean;
  lidarr_link?: boolean;
}

/** One entry of the sensors' `items` attribute. */
export interface AlbumItem {
  artist?: string | null;
  album?: string | null;
  added?: string | null;
  cover_url?: string | null;
  musicbrainz_id?: string | null;
  lidarr_url?: string | null;
}

export interface ArtistItem {
  artist?: string | null;
  added?: string | null;
  image_url?: string | null;
  musicbrainz_id?: string | null;
  lidarr_url?: string | null;
}

export const MA_DOMAIN = "music_assistant";

/** Music Assistant players, by registry platform. */
export function maPlayers(hass: Hass): string[] {
  return Object.values(hass.entities ?? {})
    .filter(
      (entry): entry is HassEntityRegistryEntry =>
        entry !== undefined &&
        entry.platform === MA_DOMAIN &&
        entry.entity_id.startsWith("media_player.") &&
        hass.states[entry.entity_id] !== undefined,
    )
    .map((entry) => entry.entity_id)
    .sort((a, b) => friendlyName(hass, a).localeCompare(friendlyName(hass, b)));
}

export function musicAssistantAvailable(hass: Hass): boolean {
  return hass.services?.[MA_DOMAIN]?.play_media !== undefined;
}

export function friendlyName(hass: Hass, entityId: string): string {
  const name = hass.states[entityId]?.attributes.friendly_name;
  return typeof name === "string" && name ? name : entityId;
}

/**
 * The player to use without asking: the helper's current value if it names a
 * player, otherwise the fixed player. Undefined means "ask each time".
 */
export function resolvePlayer(hass: Hass, config: CardConfig): string | undefined {
  if (config.player_entity) {
    const value = hass.states[config.player_entity]?.state?.trim();
    if (value && value !== "unknown" && value !== "unavailable") {
      if (value.startsWith("media_player.") && hass.states[value]) {
        return value;
      }
      // An input_select of friendly names works too.
      const byName = maPlayers(hass).find(
        (id) => friendlyName(hass, id).toLowerCase() === value.toLowerCase(),
      );
      if (byName) {
        return byName;
      }
    }
  }
  if (config.player && hass.states[config.player]) {
    return config.player;
  }
  return undefined;
}

export function items<T>(hass: Hass, entityId: string | undefined, max?: number): T[] | undefined {
  if (!entityId) {
    return undefined;
  }
  const value = hass.states[entityId]?.attributes.items;
  if (!Array.isArray(value)) {
    return undefined;
  }
  return (max ? value.slice(0, max) : value) as T[];
}

const UNITS: [Intl.RelativeTimeFormatUnit, number][] = [
  ["year", 365 * 24 * 3600],
  ["month", 30 * 24 * 3600],
  ["week", 7 * 24 * 3600],
  ["day", 24 * 3600],
  ["hour", 3600],
  ["minute", 60],
];

/** "2h ago", "yesterday", "3w ago" in the user's language. */
export function relativeTime(iso: string | null | undefined, language: string, now = Date.now()): string {
  if (!iso) {
    return "";
  }
  const then = Date.parse(iso);
  if (Number.isNaN(then)) {
    return "";
  }
  const seconds = Math.max(0, (now - then) / 1000);
  let format: Intl.RelativeTimeFormat;
  try {
    format = new Intl.RelativeTimeFormat(language, { numeric: "auto", style: "narrow" });
  } catch {
    format = new Intl.RelativeTimeFormat("en", { numeric: "auto", style: "narrow" });
  }
  for (const [unit, size] of UNITS) {
    if (seconds >= size) {
      return format.format(-Math.floor(seconds / size), unit);
    }
  }
  return format.format(0, "minute");
}

/** Up to two initials, ignoring a leading "The". */
export function initials(name: string | null | undefined): string {
  const words = (name ?? "")
    .replace(/^the\s+/i, "")
    .split(/[\s\-_/&+]+/u)
    .filter((word) => /[\p{L}\p{N}]/u.test(word));
  const letters = words.slice(0, 2).map((word) => [...word.replace(/[^\p{L}\p{N}]/gu, "")][0] ?? "");
  return letters.join("").toUpperCase() || "?";
}

export function errorMessage(err: unknown): string {
  if (err && typeof err === "object" && "message" in err && typeof err.message === "string") {
    return err.message;
  }
  return String(err);
}
