// Bundles the card, including Lit, into a single file served by the integration.
import { readFileSync } from "node:fs";
import { build } from "esbuild";

const manifest = JSON.parse(
  readFileSync(
    new URL("../custom_components/lidarr_recently_added/manifest.json", import.meta.url),
  ),
);

await build({
  entryPoints: ["src/lidarr-recently-added-card.ts"],
  outfile: "../custom_components/lidarr_recently_added/frontend/lidarr-recently-added-card.js",
  bundle: true,
  format: "esm",
  target: "es2021",
  minify: true,
  // Keeps Lit's licence notice in the bundle.
  legalComments: "eof",
  define: { __CARD_VERSION__: JSON.stringify(manifest.version) },
  banner: {
    js: `/* Lidarr Recently Added card ${manifest.version} - built from frontend/src, do not edit. */`,
  },
  logLevel: "info",
});
