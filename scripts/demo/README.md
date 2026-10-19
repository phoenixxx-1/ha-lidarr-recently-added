# Demo environment

Development tooling for screenshots and manual testing of the card. Nothing
here is shipped with the integration.

- `fake_lidarr.py`: a stand-in Lidarr API with fictional artists and generated
  artwork, including artists whose image `remoteUrl` is a path inside Lidarr
  and artists with no images.
- `custom_components/music_assistant/`: a stand-in for Music Assistant with
  three players and a `play_media` action. It fails for the album "Lanterns"
  so the card's error message can be seen. Never install it in a real Home
  Assistant: it replaces the real Music Assistant integration.
- `provision.py`: onboards a fresh Home Assistant, adds the integration
  through its config flow and saves a demo dashboard.

```sh
# 1. A config directory with the integration and the stand-in
mkdir -p demo/custom_components
ln -s "$PWD/custom_components/lidarr_recently_added" demo/custom_components/
cp -r scripts/demo/custom_components/music_assistant demo/custom_components/
printf 'frontend:\nconfig:\nlovelace:\nmusic_assistant:\n' > demo/configuration.yaml

# 2. Start the fake Lidarr and Home Assistant
python scripts/demo/fake_lidarr.py 8686 &
hass -c demo &

# 3. Onboard, add the integration, save the dashboard
(cd scripts/demo && python provision.py http://127.0.0.1:8123 /tmp/tokens.json)

# 4. Screenshots (light and dark, phone and desktop)
(cd frontend && node scripts/screenshots.mjs /tmp/tokens.json ../docs/screenshots-png)
```
