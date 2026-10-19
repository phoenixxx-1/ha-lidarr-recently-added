// Hold menu and player picker. Rendered on document.body so dashboard
// containers (scrolling sections, transforms) can't clip or offset it. Theme
// variables are set on <html> by Home Assistant, so they still apply here.

import { LitElement, css, html, nothing, svg } from "lit";

import { defineWhenReady } from "./define";

export interface PopupEntry {
  label: string;
  icon?: string;
  secondary?: string;
  checked?: boolean;
  action: () => void;
}

export interface PopupOptions {
  heading: string;
  subheading?: string;
  entries: PopupEntry[];
  /** Where the pointer was, in viewport coordinates. */
  x: number;
  y: number;
  returnFocus?: HTMLElement;
}

const TAG = "lidarr-recently-added-popup";
const SHEET_BREAKPOINT = 600;

export class LidarrRecentlyAddedPopup extends LitElement {
  static override properties = {
    heading: { type: String },
    subheading: { type: String },
    entries: { attribute: false },
    x: { type: Number },
    y: { type: Number },
  };

  heading = "";
  subheading?: string;
  entries: PopupEntry[] = [];
  x = 0;
  y = 0;
  returnFocus?: HTMLElement;

  private onKeydown = (event: KeyboardEvent): void => this.handleKeydown(event);

  override connectedCallback(): void {
    super.connectedCallback();
    document.addEventListener("keydown", this.onKeydown, true);
  }

  override disconnectedCallback(): void {
    super.disconnectedCallback();
    document.removeEventListener("keydown", this.onKeydown, true);
  }

  close(): void {
    this.remove();
    this.returnFocus?.focus({ preventScroll: true });
  }

  private get sheet(): boolean {
    return window.innerWidth < SHEET_BREAKPOINT;
  }

  protected override firstUpdated(): void {
    const panel = this.renderRoot.querySelector<HTMLElement>(".panel");
    if (panel && !this.sheet) {
      // Keep the menu on screen, next to where the user pressed.
      const margin = 8;
      const { width, height } = panel.getBoundingClientRect();
      const left = Math.min(Math.max(this.x, margin), window.innerWidth - width - margin);
      const top =
        this.y + height + margin > window.innerHeight
          ? Math.max(margin, this.y - height)
          : this.y;
      panel.style.left = `${left}px`;
      panel.style.top = `${top}px`;
    }
    panel?.classList.add("open");
    this.items()[0]?.focus({ preventScroll: true });
  }

  private items(): HTMLElement[] {
    return [...this.renderRoot.querySelectorAll<HTMLElement>(".item")];
  }

  private handleKeydown(event: KeyboardEvent): void {
    const items = this.items();
    const index = items.indexOf((this.renderRoot as ShadowRoot).activeElement as HTMLElement);
    if (event.key === "Escape") {
      event.stopPropagation();
      event.preventDefault();
      this.close();
    } else if (event.key === "ArrowDown" || event.key === "ArrowUp") {
      event.preventDefault();
      const step = event.key === "ArrowDown" ? 1 : -1;
      items[(index + step + items.length) % items.length]?.focus();
    } else if (event.key === "Tab") {
      // Keep focus inside the menu while it's open.
      event.preventDefault();
      const step = event.shiftKey ? -1 : 1;
      items[(index + step + items.length) % items.length]?.focus();
    }
  }

  private choose(entry: PopupEntry): void {
    this.close();
    entry.action();
  }

  protected override render() {
    return html`
      <div class="backdrop" @click=${() => this.close()}></div>
      <div
        class="panel ${this.sheet ? "sheet" : "menu"}"
        role="menu"
        aria-label=${this.heading}
      >
        <div class="heading">
          <div class="title">${this.heading}</div>
          ${this.subheading ? html`<div class="subtitle">${this.subheading}</div>` : nothing}
        </div>
        ${this.entries.map(
          (entry) => html`
            <button
              class="item"
              role=${entry.checked === undefined ? "menuitem" : "menuitemradio"}
              aria-checked=${entry.checked === undefined ? nothing : String(entry.checked)}
              @click=${() => this.choose(entry)}
            >
              ${entry.icon
                ? html`<svg class="icon" viewBox="0 0 24 24" aria-hidden="true">
                    ${svg`<path d=${entry.icon}></path>`}
                  </svg>`
                : nothing}
              <span class="label">
                <span>${entry.label}</span>
                ${entry.secondary
                  ? html`<span class="secondary">${entry.secondary}</span>`
                  : nothing}
              </span>
            </button>
          `,
        )}
      </div>
    `;
  }

  static override styles = css`
    :host {
      position: fixed;
      inset: 0;
      z-index: 10;
      font-family: var(--ha-font-family-body, var(--paper-font-body1_-_font-family, inherit));
      -webkit-font-smoothing: antialiased;
    }
    .backdrop {
      position: absolute;
      inset: 0;
      background: transparent;
    }
    .panel {
      position: absolute;
      box-sizing: border-box;
      min-width: 220px;
      max-width: min(320px, calc(100vw - 16px));
      padding: 6px 0;
      background: var(--card-background-color, var(--ha-card-background, #fff));
      color: var(--primary-text-color);
      border: 1px solid var(--divider-color, rgba(127, 127, 127, 0.2));
      border-radius: var(--ha-card-border-radius, 12px);
      box-shadow: 0 8px 28px rgba(0, 0, 0, 0.28);
      opacity: 0;
      transform: scale(0.96);
      transform-origin: top left;
      transition:
        opacity 120ms ease-out,
        transform 120ms ease-out;
    }
    .panel.open {
      opacity: 1;
      transform: none;
    }
    .sheet {
      left: 8px;
      right: 8px;
      bottom: 8px;
      max-width: none;
      padding-bottom: calc(6px + env(safe-area-inset-bottom, 0px));
      transform: translateY(16px);
    }
    .backdrop:has(+ .sheet) {
      background: rgba(0, 0, 0, 0.32);
    }
    .heading {
      padding: 8px 16px 6px;
    }
    .title {
      font-size: 14px;
      font-weight: 500;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    .subtitle {
      font-size: 12px;
      color: var(--secondary-text-color);
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    .item {
      display: flex;
      align-items: center;
      gap: 16px;
      width: 100%;
      min-height: 44px;
      padding: 6px 16px;
      border: 0;
      background: none;
      color: inherit;
      font: inherit;
      font-size: 14px;
      text-align: start;
      cursor: pointer;
    }
    .item:hover,
    .item:focus-visible {
      background: color-mix(in srgb, var(--primary-text-color) 8%, transparent);
      outline: none;
    }
    .item[aria-checked="true"] {
      color: var(--primary-color);
    }
    .icon {
      flex: none;
      width: 22px;
      height: 22px;
      fill: var(--secondary-text-color);
    }
    .item[aria-checked="true"] .icon {
      fill: var(--primary-color);
    }
    .label {
      display: flex;
      flex-direction: column;
      min-width: 0;
    }
    .label > span {
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    .secondary {
      font-size: 12px;
      color: var(--secondary-text-color);
    }
    @media (prefers-reduced-motion: reduce) {
      .panel {
        transition: none;
      }
    }
  `;
}

defineWhenReady(TAG, LidarrRecentlyAddedPopup);

export function openPopup(options: PopupOptions): LidarrRecentlyAddedPopup {
  document.querySelectorAll(TAG).forEach((existing) => existing.remove());
  const popup = document.createElement(TAG) as LidarrRecentlyAddedPopup;
  popup.heading = options.heading;
  popup.subheading = options.subheading;
  popup.entries = options.entries;
  popup.x = options.x;
  popup.y = options.y;
  popup.returnFocus = options.returnFocus;
  document.body.appendChild(popup);
  return popup;
}
