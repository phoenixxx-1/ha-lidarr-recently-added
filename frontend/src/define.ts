// Safe custom element registration for a card loaded with add_extra_js_url.
//
// Home Assistant's frontend installs a scoped custom element registry
// polyfill as the first thing app.js does, replacing window.customElements.
// Extra modules are imported in parallel with app.js, so they can run before
// that happens, and anything defined in the old registry is then invisible to
// Home Assistant ("Custom element doesn't exist"). So when this runs inside
// Home Assistant, wait until Home Assistant's own <home-assistant> element is
// defined in the current registry before defining ours.

const POLL_MS = 25;
const GIVE_UP_MS = 30_000;

function appReady(): boolean {
  return (
    document.querySelector("home-assistant") === null ||
    customElements.get("home-assistant") !== undefined
  );
}

export function defineWhenReady(tag: string, element: CustomElementConstructor): void {
  const define = () => {
    // Read the global each time: it may have been replaced since load.
    if (!customElements.get(tag)) {
      customElements.define(tag, element);
    }
  };
  if (appReady()) {
    define();
    return;
  }
  const started = Date.now();
  const check = () => {
    if (appReady() || Date.now() - started > GIVE_UP_MS) {
      define();
    } else {
      window.setTimeout(check, POLL_MS);
    }
  };
  check();
}
