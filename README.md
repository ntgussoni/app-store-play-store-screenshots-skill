# app-store-play-store-screenshots-skill

> A Claude Code plugin that automates App Store & Google Play screenshot creation for Expo / React Native apps — from raw simulator to store-ready marketing assets.

---

## How it works

Just tell Claude you want screenshots and it handles the full pipeline:

| Phase | What happens |
|-------|-------------|
| **Discover** | Reads your `app/` directory and understands your screens |
| **Plan** | Proposes screenshot concepts with headlines matched to your branding |
| **Capture** | Drives the iOS Simulator and Android Emulator via Maestro flows |
| **Frame** | Wraps devices with `fastlane frameit` frames |
| **Compose** | Layers gradient backgrounds, marketing text, device glow, and particle effects |
| **Export** | Outputs final PNGs at exact store-required dimensions |

---

## Install

```
/plugin marketplace add ntgussoni/app-store-play-store-screenshots-skill
/plugin install appstore-screenshots@appstore-screenshots
```

Then just ask Claude:

```
Create App Store screenshots for my app
```

Or invoke directly:

```
/appstore-screenshots:appstore-screenshots
```

---

## Output sizes

| Store | Device | Canvas size |
|-------|--------|-------------|
| App Store | iPhone 6.9" | 1290 × 2796 |
| App Store | iPad 13" | 2064 × 2752 |
| Play Store | Phone | 1080 × 1920+ |
| Play Store | Feature Graphic | 1024 × 500 |

---

## Requirements

Install these once before running the skill:

```bash
# Maestro — UI automation
curl -Ls "https://get.maestro.mobile.dev" | bash

# fastlane — device frames
gem install fastlane
fastlane frameit download_frames

# ImageMagick 7 — image processing
brew install imagemagick

# Pillow — compositor
pip3 install Pillow
```

Also needed: **Xcode + iOS Simulator**, and optionally **Android SDK** for Play Store screenshots.

---

## Scripts

The plugin ships two standalone scripts you can also use directly:

### `scripts/compose.py`

Composites a framed device screenshot onto a branded marketing canvas.

```bash
python3 scripts/compose.py \
  --screenshot path/to/framed.png \
  --output out/01_hero.png \
  --size 1290x2796 \
  --bg-color "#181020" \
  --bg-gradient "#2A1B33" \
  --headline "Drift off in minutes" \
  --subheadline "Calming stories for adults" \
  --headline-color "#c6bfff" \
  --device-glow "#6b5b9e" \
  --particles 50
```

| Flag | Default | Description |
|------|---------|-------------|
| `--screenshot` | — | Framed device PNG (omit for text-only feature graphic) |
| `--size` | required | Canvas dimensions, e.g. `1290x2796` |
| `--bg-color` | required | Background hex color |
| `--bg-gradient` | — | Gradient end color |
| `--headline` | required | Marketing headline |
| `--subheadline` | — | Supporting text below the headline |
| `--headline-color` | `#FFFFFF` | Headline hex color |
| `--font` | system font | Path to a `.ttf` file |
| `--device-scale` | `0.72` | Device width as a fraction of canvas width |
| `--device-glow` | — | Soft bloom behind the device |
| `--particles` | `0` | Ambient background dots (40–80 is a good range) |
| `--bg-image` | — | Background photo, cover-cropped to canvas |
| `--bg-overlay-opacity` | `0.55` | Darkness of the overlay over the background image |

### `scripts/launch_simulators.sh`

Boots iPhone 16 Pro Max and an Android AVD, then waits until both are ready.

```bash
bash scripts/launch_simulators.sh [android_avd_name]
```

---

## Skill reference

See [`skills/appstore-screenshots/SKILL.md`](skills/appstore-screenshots/SKILL.md) for the full spec — all five phases, Maestro flow examples, common failure fixes, and every parameter explained.

---

## License

MIT © [Nicolas Torres](https://github.com/ntgussoni)
