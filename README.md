# appstore-screenshots

A Claude Code skill that automates App Store and Google Play screenshot creation for Expo/React Native apps on Mac.

## What it does

Full pipeline from raw app screens to store-ready marketing assets:

1. **Discovers** your app's screens via Expo Router file structure
2. **Plans** screenshot concepts with headlines tuned to your app's branding
3. **Captures** screenshots via [Maestro](https://maestro.mobile.dev/) automation on iOS Simulator and Android Emulator
4. **Frames** devices using `fastlane frameit`
5. **Composites** marketing overlays — gradient backgrounds, headline text, device glow, particle effects
6. **Exports** at correct sizes for both stores

## Requirements

- macOS
- Xcode + iOS Simulator
- [Maestro](https://maestro.mobile.dev/) (`~/.maestro/bin/maestro`)
- [fastlane](https://fastlane.tools/) (`gem install fastlane`)
- ImageMagick 7 (`brew install imagemagick`)
- Python 3 + Pillow (`pip3 install Pillow`)
- Android SDK (optional, for Play Store screenshots)

## Output sizes

| Store | Device | Size |
|-------|--------|------|
| App Store | iPhone 6.9" | 1290×2796 |
| App Store | iPad 13" | 2064×2752 |
| Play Store | Phone | 1080×1920+ |
| Play Store | Feature Graphic | 1024×500 |

## Usage

Install via Claude Code:

```bash
# From your Expo project root, ask Claude:
# "Create App Store screenshots for my app"
```

Or use the scripts directly:

```bash
# Launch simulators
bash scripts/launch_simulators.sh

# Compose a screenshot
python3 scripts/compose.py \
  --screenshot path/to/framed_device.png \
  --output output/01_hero.png \
  --size 1290x2796 \
  --bg-color "#181020" \
  --bg-gradient "#2A1B33" \
  --headline "Drift off in minutes" \
  --subheadline "Calming stories for adults" \
  --headline-color "#c6bfff" \
  --device-glow "#6b5b9e" \
  --particles 50
```

## Scripts

- **`scripts/compose.py`** — Pillow compositor: canvas + gradient + device frame + headline text + glow + particles
- **`scripts/launch_simulators.sh`** — Boots iPhone 16 Pro Max + Android AVD and waits until ready

## Skill definition

See [`SKILL.md`](SKILL.md) for the full Claude Code skill spec — covers all phases, Maestro flow examples, troubleshooting, and parameter reference.

## License

MIT
