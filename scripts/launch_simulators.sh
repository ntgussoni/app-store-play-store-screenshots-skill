#!/bin/bash
# Launch iOS Simulator (iPhone 16 Pro Max) and Android Emulator
# Usage: bash launch_simulators.sh [android_avd_name]

set -e

IOS_DEVICE="iPhone 16 Pro Max"
ANDROID_AVD="${1:-}"

# ── iOS Simulator ─────────────────────────────────────────────────────────────

echo "→ Booting iOS Simulator: $IOS_DEVICE"

IOS_UDID=$(xcrun simctl list devices available | grep "$IOS_DEVICE" | head -1 | grep -oE '[A-F0-9-]{36}')

if [ -z "$IOS_UDID" ]; then
  echo "  iPhone 16 Pro Max not found. Trying any modern iPhone..."
  IOS_UDID=$(xcrun simctl list devices available | grep -E "iPhone 1[5-9]|iPhone 1[0-9] Pro" | head -1 | grep -oE '[A-F0-9-]{36}')
  if [ -z "$IOS_UDID" ]; then
    echo "  ERROR: No suitable iPhone simulator found. Create one in Xcode → Window → Devices and Simulators."
    exit 1
  fi
fi

STATE=$(xcrun simctl list devices | grep "$IOS_UDID" | grep -oE 'Booted|Shutdown' | head -1)

if [ "$STATE" = "Booted" ]; then
  echo "  Already booted."
else
  xcrun simctl boot "$IOS_UDID"
  echo "  Booted."
fi

open -a Simulator

echo "  Waiting for iOS Simulator to be ready..."
for i in $(seq 1 30); do
  STATE=$(xcrun simctl list devices | grep "$IOS_UDID" | grep -oE 'Booted' | head -1)
  if [ "$STATE" = "Booted" ]; then
    echo "  Ready."
    break
  fi
  sleep 2
done

# ── Android Emulator ──────────────────────────────────────────────────────────

if ! command -v emulator &>/dev/null; then
  echo ""
  echo "→ Android emulator not found in PATH."
  echo "  Add Android SDK: export PATH=\$PATH:\$HOME/Library/Android/sdk/emulator"
  echo "  Skipping Android launch."
  exit 0
fi

echo ""
echo "→ Launching Android Emulator"

if [ -z "$ANDROID_AVD" ]; then
  ANDROID_AVD=$(emulator -list-avds 2>/dev/null | head -1)
fi

if [ -z "$ANDROID_AVD" ]; then
  echo "  ERROR: No Android AVDs found."
  echo "  Create one: Android Studio → Device Manager → Create Virtual Device → Pixel 8 → API 34."
  exit 1
fi

echo "  Using AVD: $ANDROID_AVD"

RUNNING=$(adb devices 2>/dev/null | grep "emulator" | grep "device" | head -1)
if [ -n "$RUNNING" ]; then
  echo "  Android emulator already running."
else
  nohup emulator -avd "$ANDROID_AVD" -no-snapshot-load > /tmp/emulator.log 2>&1 &
  echo "  Emulator starting (PID $!)..."
  echo "  Waiting for Android emulator (~30s)..."
  for i in $(seq 1 30); do
    READY=$(adb shell getprop sys.boot_completed 2>/dev/null | tr -d '\r')
    if [ "$READY" = "1" ]; then
      echo "  Ready."
      break
    fi
    sleep 3
  done
fi

echo ""
echo "✓ Simulators launched. Start Expo with: npx expo start"
echo "  Press 'i' for iOS, 'a' for Android."
