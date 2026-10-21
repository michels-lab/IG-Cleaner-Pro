#!/usr/bin/env bash
set -euo pipefail

# Local Developer emulator fixture uses the disposable debug signer only;
# the official publisher separately enforces production signature equality.
gradle -p android -PigcAndroidTestBuildType=developer :app:assembleDebug :app:assembleDeveloper :app:assembleDeveloperAndroidTest
public_apk="android/app/build/outputs/apk/debug/app-debug.apk"
apk="android/app/build/outputs/apk/developer/app-developer.apk"
instrumentation="android/app/build/outputs/apk/androidTest/developer/app-developer-androidTest.apk"
test -s "$public_apk"
test -s "$apk"
test -s "$instrumentation"

adb install -r "$public_apk"
adb install -r "$apk"
adb install -r "$instrumentation"

# Distinct packages must coexist after the second APK is installed.
adb shell pm list packages | tr -d '\r' > /tmp/igc-installed-developer-packages.txt
grep -Fxq 'package:com.michelslab.igcleaner.beta' /tmp/igc-installed-developer-packages.txt
grep -Fxq 'package:com.michelslab.igcleaner.developer' /tmp/igc-installed-developer-packages.txt
mkdir -p artifacts/android-developer

adb shell am instrument -w -r \
  -e class com.michelslab.igcleaner.DeveloperEditionTest \
  com.michelslab.igcleaner.developer.test/androidx.test.runner.AndroidJUnitRunner \
  | tee artifacts/android-developer/instrumentation.txt
grep -Fq 'OK (2 tests)' artifacts/android-developer/instrumentation.txt

unzip -p "$apk" assets/ig_cleaner_pro_v120_27_synced_companion.html > /tmp/igc-developer-embedded.html
grep -Fq 'igcDevSaveNote' /tmp/igc-developer-embedded.html
cp "$apk" artifacts/android-developer/app-developer.apk
echo 'PASS: public beta and Developer install side by side; real WebView Account route, persistent section note and native JSON export'
