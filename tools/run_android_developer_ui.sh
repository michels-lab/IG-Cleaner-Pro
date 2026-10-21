#!/usr/bin/env bash
set -euo pipefail

gradle -p android -PigcAndroidTestBuildType=developer :app:assembleDebug :app:assembleDeveloper :app:assembleDeveloperAndroidTest
apk="android/app/build/outputs/apk/developer/app-developer.apk"
instrumentation="android/app/build/outputs/apk/androidTest/developer/app-developer-androidTest.apk"
test -s "$apk"
test -s "$instrumentation"

adb install -r android/app/build/outputs/apk/debug/app-debug.apk
adb install -r "$apk"
adb install -r "$instrumentation"
adb shell pm list packages | grep -q '^package:com.michelslab.igcleaner.developer
mkdir -p artifacts/android-developer

adb shell am instrument -w -r \
  -e class com.michelslab.igcleaner.DeveloperEditionTest \
  com.michelslab.igcleaner.developer.test/androidx.test.runner.AndroidJUnitRunner \
  | tee artifacts/android-developer/instrumentation.txt
grep -Fq 'OK (2 tests)' artifacts/android-developer/instrumentation.txt

unzip -p "$apk" assets/ig_cleaner_pro_v120_27_synced_companion.html > /tmp/igc-developer-embedded.html
grep -Fq 'igcDevSaveNote' /tmp/igc-developer-embedded.html
cp "$apk" artifacts/android-developer/app-developer.apk
echo 'PASS: installed Android Developer APK, real Account route, persistent section annotation and native JSON export'

adb shell pm list packages | grep -q '^package:com.michelslab.igcleaner.beta
mkdir -p artifacts/android-developer

adb shell am instrument -w -r \
  -e class com.michelslab.igcleaner.DeveloperEditionTest \
  com.michelslab.igcleaner.developer.test/androidx.test.runner.AndroidJUnitRunner \
  | tee artifacts/android-developer/instrumentation.txt
grep -Fq 'OK (2 tests)' artifacts/android-developer/instrumentation.txt

unzip -p "$apk" assets/ig_cleaner_pro_v120_27_synced_companion.html > /tmp/igc-developer-embedded.html
grep -Fq 'igcDevSaveNote' /tmp/igc-developer-embedded.html
cp "$apk" artifacts/android-developer/app-developer.apk
echo 'PASS: installed Android Developer APK, real Account route, persistent section annotation and native JSON export'

# Installing Developer must not replace the other already-installed variant.
mkdir -p artifacts/android-developer

adb shell am instrument -w -r \
  -e class com.michelslab.igcleaner.DeveloperEditionTest \
  com.michelslab.igcleaner.developer.test/androidx.test.runner.AndroidJUnitRunner \
  | tee artifacts/android-developer/instrumentation.txt
grep -Fq 'OK (2 tests)' artifacts/android-developer/instrumentation.txt

unzip -p "$apk" assets/ig_cleaner_pro_v120_27_synced_companion.html > /tmp/igc-developer-embedded.html
grep -Fq 'igcDevSaveNote' /tmp/igc-developer-embedded.html
cp "$apk" artifacts/android-developer/app-developer.apk
echo 'PASS: installed Android Developer APK, real Account route, persistent section annotation and native JSON export'
