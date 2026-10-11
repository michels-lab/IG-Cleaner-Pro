#!/usr/bin/env bash
set -euo pipefail

gradle -p android :app:assembleDebug :app:assembleDebugAndroidTest
adb install -r android/app/build/outputs/apk/debug/app-debug.apk
adb install -r android/app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk
mkdir -p artifacts/visual/android

for viewport in compact wide; do
  if [[ "$viewport" == compact ]]; then
    adb shell wm size 720x1280
    adb shell wm density 320
  else
    adb shell wm size 1080x1920
    adb shell wm density 320
  fi
  sleep 3
  if ! adb shell am instrument -w -r -e viewport "$viewport" \
     com.michelslab.igcleaner.beta.test/androidx.test.runner.AndroidJUnitRunner \
     | tee "artifacts/visual/android/instrumentation-$viewport.txt"; then
    adb logcat -d -t 200 | tail -100 || true
    exit 1
  fi
  if ! grep -Eq 'OK \(8 tests\)' "artifacts/visual/android/instrumentation-$viewport.txt"; then
    echo "::error::Android UI instrumentation did not report success for $viewport"
    adb logcat -d -t 200 | tail -100 || true
    exit 1
  fi
done

adb pull /sdcard/Android/data/com.michelslab.igcleaner.beta/files/igc-ui-capture/ artifacts/visual/android/
test "$(find artifacts/visual/android/igc-ui-capture -name '*.png' | wc -l)" -eq 8
echo 'SUCCESS: eight instrumented Android Home and About screenshots captured'
