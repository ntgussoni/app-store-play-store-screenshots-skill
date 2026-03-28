---
name: appstore-screenshots
description: "Automate App Store and Play Store screenshot creation for Expo/React Native apps on Mac. Handles the full pipeline: discover app screens, confirm branding with the user, plan screenshot concepts, capture screenshots via Maestro automation on iOS Simulator and Android Emulator, add device frames, composite marketing text and backgrounds, and export at correct sizes for both stores. Use this skill whenever someone wants to create, generate, automate, or update App Store screenshots, Play Store screenshots, store listings, marketing screenshots, or app store assets — even if they don't say 'screenshots' explicitly. Trigger on phrases like 'prepare store assets', 'get the app ready for the store', 'update the listing', 'create marketing images', etc."
---

# App Store Screenshot Automation

Full pipeline for creating App Store (iOS) and Google Play Store (Android) screenshots for Expo/React Native apps on Mac.

## Store Requirements

| Store | Device | Size | Format | Count |
|-------|--------|------|--------|-------|
| App Store | iPhone 6.9" | 1290×2796 | PNG/JPG, no alpha | 2–10 |
| App Store | iPad 13" | 2064×2752 | PNG/JPG, no alpha | 2–10 (required if app supports iPad) |
| Play Store | Phone | 1080×1920 min | PNG/JPEG, no alpha | 4–10 |
| Play Store | Feature Graphic | 1024×500 | PNG/JPEG, no alpha | exactly 1 |

---

## Phase 1: Discovery & Planning

### 1.1 — How many screenshots?

Ask: *"How many screenshots do you want? iOS requires at least 2, Android at least 4 — five is a typical sweet spot."*

### 1.2 — Screenshot concepts

Ask: *"Do you have specific screens in mind, or should I explore the app and propose concepts?"*

**If the user provides concepts** — confirm them back. If they gave fewer than the count they asked for (e.g., 3 concepts but want 5 screenshots), flag the gap and ask or suggest the missing ones.

**If you're suggesting concepts:**
1. Read the `app/` directory — Expo Router uses file-based routing, so filenames map directly to routes
2. Read `package.json` and the home screen to understand what the app does
3. Propose N concepts in a table:

| # | Goal | Headline | Target screen |
|---|------|----------|---------------|
| 1 | Value proposition | "Drift off in minutes" | `/(tabs)/index` |
| 2 | Key feature | "Narrated by real voices" | `/(tabs)/stories` |

4. Ask for confirmation or changes before continuing — the concept plan drives everything downstream.

### 1.3 — Brand

Explore the codebase for design tokens: theme files, `_layout.tsx`, constants, Tailwind config. Find:
- Background color or gradient
- Primary / accent color
- Headline font
- Overall mood (dark/light)

Present a brief summary, confirm with the user, then apply those values throughout composition.

### 1.4 — iPad?

Check `app.json` for `ios.supportsTablet: true`. If present, the App Store requires iPad screenshots (2064×2752) — confirm with the user.

---

## Phase 2: Setup

### 2.1 — Dependencies

```bash
# Maestro is often NOT on PATH after install — check both locations
which maestro 2>/dev/null || ls ~/.maestro/bin/maestro

which fastlane && fastlane --version     # device frames
magick --version                         # ImageMagick 7 (use `magick`, not `convert`)
which adb                                # Android screenshot capture
python3 -c "import PIL; print('Pillow OK')"
xcrun simctl list devices | grep "iPhone 16 Pro Max"
```

Install anything missing:
```bash
curl -Ls "https://get.maestro.mobile.dev" | bash   # Maestro
gem install fastlane
brew install imagemagick android-platform-tools
pip3 install Pillow
```

> Maestro installs to `~/.maestro/bin/maestro`. Add `~/.maestro/bin` to PATH, or use the full path in every command.

**Download frameit device frames** (do this once):
```bash
fastlane frameit download_frames
```

> This downloads all available Apple and Google device frame PNGs to `~/.fastlane/frameit/latest/`. Without it, frameit won't find any frames. Run it after installing fastlane or if frames seem outdated.

### 2.2 — Launch simulators

```bash
bash <skill_dir>/scripts/launch_simulators.sh
```

This boots iPhone 16 Pro Max (needed for 1290×2796 output) and the first available Android AVD, then waits until both are ready.

No Android AVD? Create one: AVD Manager → Create Virtual Device → Pixel 8 → API 34.

### 2.3 — Start Expo

If the dev server isn't running:
```bash
npx expo start
# press i for iOS, a for Android
```

Wait until the app is fully loaded on both simulators before starting captures.

**If the app fetches data from a local backend** (e.g., a Next.js server), make sure it's running too. The Android emulator can't use `localhost` — it needs the machine's LAN IP (e.g., `http://192.168.x.x:3000`). Check what the app's API URL is configured to (often in `lib/api.ts` or similar). If that IP is hardcoded and your machine's IP has changed, screens that load data will show "Failed to connect" errors during capture. Fix by updating the IP before running flows.

---

## Phase 3: Capture Screenshots

### 3.1 — Determine the Maestro app ID

The right `appId` depends on how the app is running:

| Platform | Running mode | `appId` to use |
|---|---|---|
| iOS | Expo Go (default `expo start`) | `host.exp.Exponent` (capital E) |
| iOS | Standalone / dev-client build | `ios.bundleIdentifier` from `app.json` |
| Android | Expo Go (default `expo start`) | `host.exp.exponent` (all lowercase) |
| Android | Standalone / dev-client build | `android.package` from `app.json` |

> The case difference matters: iOS Expo Go is `host.exp.Exponent`, Android Expo Go is `host.exp.exponent`.

If unsure, ask: *"Are you using Expo Go, or did you build a custom binary?"*

### 3.2 — Get the iOS simulator UDID

```bash
xcrun simctl list devices | grep "iPhone 16 Pro Max"
```

Copy the UDID — pass it as `--device <UDID>` to every Maestro command for iOS. Without it, Maestro may default to the Android emulator when both are running.

For Android, Maestro auto-detects the emulator. You can also pass `--device emulator-5554` explicitly.

### 3.3 — Write Maestro flows

Organize flows by platform under `screenshots/maestro-flows/`:

```
screenshots/
  maestro-flows/
    ios/
      01_home_hero.yaml
      02_stories_library.yaml
      ...
    android/
      01_home_hero.yaml
      02_stories_library.yaml
      ...
```

```bash
mkdir -p screenshots/maestro-flows/ios screenshots/maestro-flows/android
```

Run Maestro **from the `screenshots/` directory** — that's where `takeScreenshot` saves files. iOS and Android flows share the same concept names (01–05) but differ in `appId`, host, and any platform-specific navigation.

#### Deep link navigation (primary strategy)

The most reliable way to navigate in Expo Go is via deep link — it goes directly to any route without touching the tab bar:

```yaml
# iOS (Expo Go on Simulator)
- openLink: "exp://localhost:8081/--/(tabs)/stories"

# Android (Expo Go on Emulator — use 10.0.2.2, not localhost)
- openLink: "exp://10.0.2.2:8081/--/(tabs)/stories"
```

URL format: `exp://<host>:<port>/--/<expo-router-path>`
- iOS simulator host: `localhost`
- Android emulator host: `10.0.2.2` (the emulator's alias for the host machine)
- Default Metro port: `8081`
- Path mirrors `app/` directory: `app/(tabs)/stories.tsx` → `/--/(tabs)/stories`
- The index route (`app/(tabs)/index.tsx`) is special — **do not use `/--/(tabs)/index`**. Use the root URL `exp://10.0.2.2:8081` (Android) or `exp://localhost:8081` (iOS) instead. `/--/(tabs)/index` will show a 404 "This screen doesn't exist" error.

Deep links sidestep two major Expo Go hazards:
- The **floating Tools button** in the bottom-right corner, which intercepts taps on the rightmost tab
- **Tab label text matching failures** — `tapOn: text: "Stories"` matches section headers and other elements, not just the tab

#### Deep linking to detail/nested screens

If a screenshot requires tapping into a detail screen (e.g., a story page or audio player), deep link there directly instead of tapping cards on screen. Inspect the `app/` directory to find the route:

```yaml
# Go directly to a story detail page — avoids unreliable card taps
- openLink: "exp://10.0.2.2:8081/--/story/my-story-slug"
- waitForAnimationToEnd
- waitForAnimationToEnd
- waitForAnimationToEnd
- waitForAnimationToEnd
- tapOn:
    text: "Start Story"
```

Find real slugs by listing `posts/` or `content/` directories in the project.

#### First flow — launching the app

After tapping your app name in the Expo Go launcher, Expo Go shows a **bottom panel** ("Reload / Go home / Tools"). Any tap at `y=97%` hits this panel, not your app's tab bar. Dismiss it first:

```yaml
appId: host.exp.Exponent   # iOS; use host.exp.exponent for Android
---
- launchApp:
    clearState: false        # preserve app state between runs
- waitForAnimationToEnd
- tapOn:
    text: "MyAppName"        # select your app in the Expo Go launcher
    optional: true           # skip if already inside the app
- waitForAnimationToEnd
- waitForAnimationToEnd
- tapOn:
    text: "Continue"         # dismiss Expo Go tutorial overlay if it appears
    optional: true
- waitForAnimationToEnd
- waitForAnimationToEnd
# Tap into app content to dismiss Expo Go bottom panel
- tapOn:
    point: "50%,20%"
- waitForAnimationToEnd
# Navigate via deep link
- openLink: "exp://localhost:8081/--/(tabs)/stories"
- waitForAnimationToEnd
- waitForAnimationToEnd
- takeScreenshot: "02_stories_library"
```

#### Subsequent flows — no relaunch needed (usually)

If the simulator/emulator is still running from the previous flow, just deep link directly:

```yaml
appId: host.exp.Exponent
---
- openLink: "exp://localhost:8081/--/(tabs)/stories"
- waitForAnimationToEnd
- waitForAnimationToEnd
- takeScreenshot: "02_stories_library"
```

**Exception:** if the emulator was rebooted or Expo Go was closed between flows, it will show the app launcher instead of the app. In that case, use the full launch sequence (same as the first flow) with `launchApp`, `tapOn: text: "MyAppName"`, dismiss the bottom panel, then deep link. Using `optional: true` on the `tapOn` means the flow still works even when the app is already open.

#### Dismissing modal screens between flows

If a previous flow navigated into a detail/modal screen (e.g., an audio player, a story page), the next flow may open on top of that screen. Press Back first to return to the tab bar:

```yaml
appId: host.exp.exponent
---
- pressKey: "Back"
- waitForAnimationToEnd
- waitForAnimationToEnd
- openLink: "exp://10.0.2.2:8081/--/(tabs)/bedside"
- waitForAnimationToEnd
- waitForAnimationToEnd
- waitForAnimationToEnd
- takeScreenshot: "05_bedside"
```

#### Tab bar coordinate taps (fallback only)

If the app doesn't use Expo Router, fall back to coordinate taps — always use coordinates, not text, for tab bar items:

For a **3-tab layout**:

| Tab | Coordinate |
|---|---|
| Leftmost | `point: "15%,97%"` |
| Middle | `point: "50%,97%"` |
| Rightmost | `point: "83%,97%"` *(may be blocked by Expo Go Tools button)* |

For 4+ tabs, divide the width evenly (4 tabs → `12%`, `37%`, `62%`, `87%`).

#### Maestro command reference

```yaml
# Wait for screen transitions and animations to settle
- waitForAnimationToEnd        # use multiple in a row for slow transitions

# Scroll down to reveal content below the fold
- scroll

# Scroll until a specific element is visible
- scrollUntilVisible:
    element:
      text: "Section Title"
    direction: DOWN

# Swipe gesture
- swipe:
    start: "50%,40%"
    end: "50%,80%"

# Press hardware back button (Android — dismisses modals, goes back a screen)
- pressKey: "Back"

# Assert something is visible before screenshotting
- assertVisible:
    text: "Expected Content"
```

> **Do not use `wait: <ms>`** — this syntax is not valid in Maestro and will cause a flow failure ("Invalid Command: wait"). Use multiple `waitForAnimationToEnd` calls instead to wait for slower transitions.

### 3.4 — Run the flows

```bash
cd screenshots/

# iOS — pass UDID to avoid targeting Android emulator
~/.maestro/bin/maestro --device <iOS_UDID> test maestro-flows/ios/01_home_hero.yaml
~/.maestro/bin/maestro --device <iOS_UDID> test maestro-flows/ios/02_stories_library.yaml
# ...

# Android — emulator is auto-detected, but you can be explicit
~/.maestro/bin/maestro --device emulator-5554 test maestro-flows/android/01_home_hero.yaml
~/.maestro/bin/maestro --device emulator-5554 test maestro-flows/android/02_stories_library.yaml
# ...
```

Screenshots land in `screenshots/`. **Review each one before moving on** — read the PNG and assess it against the checklist below. Don't batch all flows and review at the end; catch problems while the simulator is still running so you can re-run a single flow instead of starting over.

### 3.5 — Review each screenshot

After every `takeScreenshot`, read the captured PNG and evaluate:

**Hard failures — recapture immediately:**
- Wrong screen (navigated to the wrong route)
- App still loading / spinner visible / skeleton UI
- "Something went wrong" or 404 error on screen
- Expo Go bottom panel ("Reload / Go home / Tools") visible
- Expo Go floating gear icon visible in the corner (see §4.2 for removal)
- Status bar shows an alert, low battery, or notification that distracts

**Quality issues — flag to the user and ask if they want to recapture:**
- Key content cut off at the bottom (suggest scrolling less or adjusting the flow)
- Screen looks too empty / not enough content loaded yet (suggest adding more `waitForAnimationToEnd`)
- Content that would be more compelling on a different screen state (e.g., a story half-played vs. just started)
- The featured story or content shown isn't representative / looks generic

**Composition suggestions — note for the compose step:**
- Lots of whitespace in a particular region (may affect how the device sits in the final layout)
- Dark vs. light content balance (very dark screenshots may get lost against the dark background)

After reviewing, tell the user:
- ✓ what looks good
- ✗ what needs to be recaptured (and why)
- 💡 any suggestions for getting a better shot

Only move screenshots to `raw/` once you're satisfied:
```bash
mv *.png raw/ios/       # after iOS runs
mv *.png raw/android/   # after Android runs
```

**Common failures and fixes:**

| Symptom | Fix |
|---|---|
| Rightmost tab tap opens Expo Go dev panel | Expo Go Tools button intercepting; use `openLink` deep link |
| Coordinate taps navigate to wrong tab | Use `openLink` deep link — bypasses tab bar entirely |
| `tapOn: text` taps the wrong element | Tab labels appear in headers too; use `openLink` or coordinate tap |
| Tab bar tap hits "Reload" or "Go home" | Expo Go bottom panel still showing; tap `50%,20%` first |
| "Continue" not found | Tutorial already dismissed — `optional: true` handles it |
| Animation still running | Add another `waitForAnimationToEnd` |
| Maestro targets wrong device | Pass `--device <UDID>` or `--device emulator-5554` explicitly |
| Screenshots saved to wrong directory | Run Maestro from the `screenshots/` directory |
| Android: "This screen doesn't exist" | Route path wrong — try root URL or check `app/` directory for exact path |
| Next flow opens on previous screen (modal) | Add `pressKey: "Back"` at the start of the flow |
| Card tap misses / "Start Story" not found | Deep link directly to the detail route instead of tapping a card |
| "Invalid Command: wait" | Replace `wait: <ms>` with `waitForAnimationToEnd` |
| Android `appId` fails | Use `host.exp.exponent` (all lowercase) for Android Expo Go |
| Screen shows "Failed to connect to server" | Backend server isn't running or LAN IP changed; check API URL in `lib/api.ts` and restart server |
| Subsequent flow shows Expo Go launcher (not the app) | Emulator restarted between flows; use the full `launchApp` + `tapOn` launch sequence |
| `/--/(tabs)/index` shows 404 "This screen doesn't exist" | The index route can't be deep linked by path — use the root URL (`exp://10.0.2.2:8081`) instead |

---

## Phase 4: Compose

### 4.1 — Device frames

Device frames are added with `fastlane frameit`. Key gotchas:

**Run `frameit` from inside the directory containing screenshots** — it does not support a `--path` flag:
```bash
cd screenshots/raw/ios/
fastlane frameit silver
```

Framed files are created as `<name>_framed.png` alongside the originals.

**iOS: iPhone 16 Pro Max is not in the frameit database.** The simulator captures at 1320×2868, which frameit doesn't recognize. Resize to 1290×2796 before framing:

```bash
cd screenshots/raw/ios/
mkdir -p resized
for f in *.png; do magick "$f" -resize 1290x2796! "resized/$f"; done
cd resized/
fastlane frameit silver
```

**Android: match screenshot size to a supported frame.** The emulator captures at native resolution (often 1080×2400). You need to resize to a size frameit knows:

| Frame | Resize to | Notes |
|---|---|---|
| Google Pixel 3 | 1080×2160 | Good choice — unambiguous |
| Google Pixel 4 | 1080×2280 | Also good |
| Google Pixel 5 | 1080×2340 | **Conflicts with iPhone 13 Mini** — avoid |

Resize and frame Android screenshots:
```bash
cd screenshots/raw/android/
mkdir -p pixel4
for f in *.png; do magick "$f" -resize 1080x2280! "pixel4/$f"; done
cd pixel4/
fastlane frameit android    # NOTE: use "android" not "silver" — frameit defaults to iOS platform
```

> **`fastlane frameit silver` will reject all Android sizes** because it defaults to iOS platform and only matches iOS resolutions. Always use `fastlane frameit android` for Android screenshots.

If frameit still reports "Unsupported screen size", run `fastlane frameit download_frames` to update the frame database.

### 4.2 — Remove Expo Go artifacts

Expo Go renders a floating blue gear/tools icon in the corner of the screen. It sometimes appears in screenshots. Remove it with ImageMagick by painting over the region with the background color.

To find the exact bounding box, scan the raw screenshot for blue pixels:
```python
from PIL import Image
img = Image.open("screenshot.png").convert("RGB")
w, h = img.size
for y in range(h):
    for x in range(w):
        r, g, b = img.getpixel((x, y))
        if b > 150 and b > r * 1.5 and b > g * 1.3:
            print(f"blue pixel at ({x}, {y})")
```

Once you have the coordinates, paint over with the app's background color:
```bash
magick screenshot.png \
  -fill "#181020" \
  -draw "rectangle x1,y1 x2,y2" \
  screenshot_clean.png
```

Add some padding around the bounding box to fully cover the icon. Then re-run frameit and compose on the cleaned screenshot.

### 4.3 — Background images (optional but high impact)

A cinematic background image transforms screenshots from good to world-class. The `--bg-image` parameter accepts any PNG/JPG — it gets cover-cropped to the canvas size and darkened with an overlay so text stays readable.

**Step 1 — check for available image generation MCPs.**
Before asking the user for images, check what MCP tools are available in the current session. Look for tools with names containing: `fal`, `replicate`, `flux`, `dalle`, `stability`, `imagen`, or similar.

If one exists, ask: *"I can generate atmospheric background images using [MCP name] — want me to? Or do you have your own images to use?"*

**If generating with an MCP**, use a prompt tuned to the app's mood. For a sleep/bedtime app:
> *"atmospheric moonlit forest at night, misty, deep indigo and violet tones, cinematic wide angle, no text, no people, photorealistic, 4k"*

One cohesive background image reused across all screenshots often looks better than five different ones — it creates a unified campaign feel.

**If no MCP is available**, ask the user to provide background images, or proceed with gradient-only (still looks good with glow + particles enabled).

Save background images to `screenshots/backgrounds/`.

### 4.4 — Marketing overlays

Run `scripts/compose.py` for each screenshot:

```bash
python3 <skill_dir>/scripts/compose.py \
  --screenshot screenshots/raw/ios/resized/01_home_framed.png \
  --output screenshots/composed/ios/01_home.png \
  --size 1290x2796 \
  --bg-color "#181020" \
  --bg-gradient "#2A1B33" \
  --headline "Drift off in minutes" \
  --subheadline "Calming stories for adults, narrated with soothing music" \
  --headline-color "#c6bfff" \
  --font "/path/to/font.ttf" \
  --device-glow "#6b5b9e" \
  --particles 50
```

When you have a background image, add:
```bash
  --bg-image screenshots/backgrounds/moonlit_forest.png \
  --bg-overlay-opacity 0.55
```
Increase `--bg-overlay-opacity` (toward `0.75`) if the text is hard to read over the image.

**Parameter reference:**

| Parameter | Default | Purpose |
|---|---|---|
| `--bg-image` | none | Background photo/AI image, cover-cropped to canvas |
| `--bg-overlay-opacity` | 0.55 | How dark the overlay over the bg image is (0=transparent, 1=black) |
| `--device-glow` | none | Soft colored bloom behind the device — use the app's accent color |
| `--particles` | 0 | Ambient star/dust dots scattered in the background — 40–80 is a good range |
| `--subheadline` | none | Supporting text below the headline — always include |

The script layers in order: gradient/bg image → dark overlay → particles → device glow → device shadow → device → text.

**Always include `--subheadline`** — screenshots without it look sparse. **Always include `--device-glow` and `--particles`** for a premium feel.

**For Android without device frames** — pass the raw (or resized) screenshot directly. The Play Store does not require device frames.

#### Review each composed screenshot

After running compose.py for each screenshot, read the output PNG and check:

**Hard failures — recompose:**
- Device frame not visible (wrong `--screenshot` path — check the file exists)
- Text overflows or is cut off at the edges
- Expo Go artifact visible inside the device frame (re-clean the raw screenshot, see §4.2)

**Quality checks — flag to the user:**
- Headline too long and wraps awkwardly (suggest shortening)
- Subheadline color blends into the background (try a slightly lighter value)
- Device sits too low and clips at the bottom (try `--device-scale 0.65`)
- Glow color clashes with the device frame (try matching the app's primary color more closely)
- Particles too dense or too sparse (adjust `--particles`)
- Background image (if used) competes with text readability (increase `--bg-overlay-opacity`)

After reviewing, show the user the composed image and give a brief verdict: what works, what could be improved, and whether it's ready for the store.

### 4.5 — Android Feature Graphic (1024×500)

```bash
python3 <skill_dir>/scripts/compose.py \
  --screenshot screenshots/raw/android/pixel4/android_01_home_framed.png \
  --output screenshots/final/android/feature_graphic.png \
  --size 1024x500 \
  --bg-color "#181020" \
  --bg-gradient "#2A1B33" \
  --headline "App Name — Tagline" \
  --headline-color "#c6bfff" \
  --font "/path/to/font.ttf"
```

Adding a `--screenshot` makes the feature graphic more visually interesting — the device image appears to the right of the headline. Omit it for a text-only graphic.

---

## Phase 5: Export

```
screenshots/final/
  ios/
    iphone/    → 1290×2796 PNG  →  App Store Connect
    ipad/      → 2064×2752 PNG  →  App Store Connect (if iPad)
  android/
    phone/     → 1080×1920+ PNG →  Google Play Console
    feature_graphic.png  →  1024×500  →  Google Play Console
```

Print a summary when done:
```
✓ iOS iPhone:      N screenshots → screenshots/final/ios/iphone/
✓ iOS iPad:        N screenshots → screenshots/final/ios/ipad/   (if applicable)
✓ Android Phone:   N screenshots → screenshots/final/android/phone/
✓ Android Feature: 1 graphic     → screenshots/final/android/feature_graphic.png

Ready to upload to App Store Connect and Google Play Console.
```

---

## Scripts

- `scripts/compose.py` — Pillow compositor: canvas + gradient + device frame + headline text
- `scripts/launch_simulators.sh` — Boot iPhone 16 Pro Max + Android AVD and wait until ready
