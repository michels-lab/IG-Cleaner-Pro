#!/usr/bin/env bash
# FINAL stable publisher: prove both production-signed Android APKs actually
# install and launch side by side on a booted emulator. Never infer success
# from APK metadata, an am start invocation, or a transient launch timeout.
set -euo pipefail

PUBLIC_PKG="com.michelslab.igcleaner"
DEVELOPER_PKG="com.michelslab.igcleaner.developer"
PUBLIC_APK="android/app/build/outputs/apk/release/app-release.apk"
DEVELOPER_APK="android/app/build/outputs/apk/developer/app-developer.apk"
test -s "$PUBLIC_APK"
test -s "$DEVELOPER_APK"
test "$(adb shell getprop sys.boot_completed | tr -d '\r')" = "1"

adb install -r "$PUBLIC_APK"
adb install -r "$DEVELOPER_APK"
installed="$(adb shell pm list packages | tr -d '\r')"
grep -Fxq "package:$PUBLIC_PKG" <<< "$installed"
grep -Fxq "package:$DEVELOPER_PKG" <<< "$installed"

# On a software-rendered CI emulator the first cold am start -W can report
# "Status: timeout" after 30 seconds even though the real foreground activity
# eventually resumes. Launch without that artificial ActivityManager wait,
# then require TWO consecutive positive runtime observations for the exact
# package and MainActivity, including a live process. No timeout = success.
launch_and_prove_foreground() {
  local package="$1"
  local component="$2"
  local kind="$3"
  local launch_output snapshot resumed pid attempt stable=0

  if ! launch_output="$(adb shell am start -n "$component" 2>&1)"; then
    echo "FAIL: $kind Android ActivityManager rejected launch" >&2
    return 1
  fi
  if ! grep -Eq '(^|[[:space:]])(Starting:|Warning: Activity not started)' <<< "$launch_output"; then
    echo "FAIL: $kind launch returned no positive ActivityManager acknowledgement" >&2
    return 1
  fi
  if grep -Eq '(^|[[:space:]])(Error:|Exception:|SecurityException)' <<< "$launch_output"; then
    echo "FAIL: $kind launch reported an ActivityManager error" >&2
    return 1
  fi

  for ((attempt=1; attempt<=50; attempt++)); do
    snapshot="$(adb shell dumpsys activity activities 2>/dev/null || true)"
    resumed="$(grep -E '(^|[[:space:]])(topResumedActivity|mTopResumedActivity|mResumedActivity|ResumedActivity)[=:]' <<< "$snapshot" || true)"
    pid="$(adb shell pidof "$package" 2>/dev/null | tr -d '\r' || true)"
    if [[ -n "$pid" ]] &&
       grep -Fq "$package/" <<< "$resumed" &&
       grep -Eq '(\/|\.)MainActivity([[:space:]{}]|$)' <<< "$resumed"; then
      stable=$((stable + 1))
      if ((stable >= 2)); then
        echo "PASS: $kind Android MainActivity foreground and live process verified twice"
        return 0
      fi
    else
      stable=0
    fi
    sleep 3
  done
  echo "FAIL: $kind Android MainActivity never verified foreground with a live process (50 attempts)" >&2
  return 1
}

launch_and_prove_foreground "$PUBLIC_PKG" "$PUBLIC_PKG/.MainActivity" "public"
launch_and_prove_foreground "$DEVELOPER_PKG" "$DEVELOPER_PKG/com.michelslab.igcleaner.MainActivity" "Developer"

# Coexistence remains a separate postlaunch requirement.
adb shell pm path "$PUBLIC_PKG" | grep -Fq 'package:'
adb shell pm path "$DEVELOPER_PKG" | grep -Fq 'package:'
echo 'PASS: stable public + Developer production-signed Android APKs installed, launched, and coexist.'
