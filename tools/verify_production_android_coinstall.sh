#!/usr/bin/env bash
# Official publisher: installed, production-signed Android package coexistence.
# Runner invokes this through /usr/bin/sh; explicitly execute with bash from
# release.yml so 'set -o pipefail' cannot fail before any APK is installed.
# This check is mandatory, never simulated or converted into a packaging-only pass.
set -euo pipefail

PUBLIC_APK="android/app/build/outputs/apk/release/app-release.apk"
DEVELOPER_APK="android/app/build/outputs/apk/developer/app-developer.apk"
test -s "$PUBLIC_APK"
test -s "$DEVELOPER_APK"
test "$(adb shell getprop sys.boot_completed | tr -d '\r')" = "1"

adb install -r "$PUBLIC_APK"
adb install -r "$DEVELOPER_APK"
adb shell pm list packages | tr -d '\r' > /tmp/installed-igc-packages.txt
grep -Fx 'package:com.michelslab.igcleaner' /tmp/installed-igc-packages.txt
grep -Fx 'package:com.michelslab.igcleaner.developer' /tmp/installed-igc-packages.txt

adb shell am start -W -n 'com.michelslab.igcleaner/.MainActivity' | tee /tmp/igc-public-launch.txt
grep -Fx 'Status: ok' /tmp/igc-public-launch.txt
adb shell am start -W -n 'com.michelslab.igcleaner.developer/com.michelslab.igcleaner.MainActivity' | tee /tmp/igc-developer-launch.txt
grep -Fx 'Status: ok' /tmp/igc-developer-launch.txt

# Verify both remain installed after the other is launched.
adb shell pm path com.michelslab.igcleaner | grep -Fq 'package:'
adb shell pm path com.michelslab.igcleaner.developer | grep -Fq 'package:'
echo 'PASS: official stable and Developer production-signed Android variants coexist and launch.'
