// Takes README screenshots of the card in a running demo Home Assistant
// (see scripts/demo). Usage:
//   node scripts/screenshots.mjs <tokens.json> <output dir>
import { mkdirSync, readFileSync } from "node:fs";
import { chromium } from "@playwright/test";

const [tokensFile, outDir] = process.argv.slice(2);
const tokens = JSON.parse(readFileSync(tokensFile, "utf8"));
const base = tokens.hassUrl;
mkdirSync(outDir, { recursive: true });

const browser = await chromium.launch(
  process.env.CHROMIUM_PATH ? { executablePath: process.env.CHROMIUM_PATH } : {},
);

const VIEWPORTS = {
  phone: { viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, isMobile: true, hasTouch: true },
  desktop: { viewport: { width: 1280, height: 860 }, deviceScaleFactor: 1 },
};

async function open(size, scheme, path) {
  const context = await browser.newContext({ ...VIEWPORTS[size], colorScheme: scheme });
  await context.addInitScript((t) => {
    localStorage.setItem("hassTokens", JSON.stringify({ ...t, expires: Date.now() + 1800_000 }));
  }, tokens);
  const page = await context.newPage();
  await page.goto(`${base}${path}`);
  const card = page.locator("lidarr-recently-added-card").first();
  await card.waitFor();
  // Wait for every visible cover to load.
  await page.waitForFunction(() => {
    const cards = [...document.querySelectorAll("home-assistant")]
      .flatMap((el) => [el]);
    const find = (root) => {
      const found = [];
      const walk = (node) => {
        if (!node) return;
        if (node.tagName === "LIDARR-RECENTLY-ADDED-CARD") found.push(node);
        node.shadowRoot && [...node.shadowRoot.children].forEach(walk);
        [...(node.children ?? [])].forEach(walk);
      };
      walk(root);
      return found;
    };
    const all = cards.flatMap(find);
    return (
      all.length > 0 &&
      all.every((c) =>
        [...c.shadowRoot.querySelectorAll("img")].every((img) => {
          // Lazy images outside the viewport never load; ignore those.
          const r = img.getBoundingClientRect();
          const visible = r.right > 0 && r.left < innerWidth && r.bottom > 0 && r.top < innerHeight;
          return !visible || (img.complete && img.naturalWidth > 0);
        }),
      )
    );
  });
  await page.waitForTimeout(800);
  return { context, page, card };
}

async function shot(page, name) {
  await page.screenshot({ path: `${outDir}/${name}.png` });
  console.log(`saved ${name}.png`);
}

for (const scheme of ["light", "dark"]) {
  for (const size of ["phone", "desktop"]) {
    const { context, page } = await open(size, scheme, "/music-demo/music");
    await shot(page, `strip-${size}-${scheme}`);
    await context.close();

    const wall = await open(size, scheme, "/music-demo/wall");
    await shot(wall.page, `wall-${size}-${scheme}`);
    await wall.context.close();
  }
}

// Hold menu (phone, as a bottom sheet) and on desktop.
for (const size of ["phone", "desktop"]) {
  const { context, page, card } = await open(size, "dark", "/music-demo/music");
  const tile = card.locator(".tile.album").first();
  await tile.click({ button: "right" });
  await page.locator("lidarr-recently-added-popup").waitFor();
  await page.waitForTimeout(300);
  await shot(page, `menu-${size}-dark`);
  await context.close();
}

// Tap to play: the toast.
{
  const { context, page, card } = await open("desktop", "light", "/music-demo/music");
  await card.locator(".tile.album").first().click();
  await page.waitForTimeout(700);
  await shot(page, "toast-desktop-light");
  // An album Music Assistant can't find shows the error.
  await card.locator(".tile.album", { hasText: "Lanterns" }).click();
  await page.waitForTimeout(700);
  await shot(page, "toast-error-desktop-light");
  await context.close();
}

// No player configured: the picker.
{
  const { context, page, card } = await open("phone", "light", "/music-demo/ask");
  await card.locator(".tile.album").first().click();
  await page.locator("lidarr-recently-added-popup").waitFor();
  await page.waitForTimeout(300);
  await shot(page, "picker-phone-light");
  await context.close();
}

await browser.close();
