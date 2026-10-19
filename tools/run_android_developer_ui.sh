#!/usr/bin/env bash
set -euo pipefail

gradle -p android -PigcAndroidTestBuildType=developer :app:assembleDeveloper :app:assembleDeveloperAndroidTest
apk="android/app/build/outputs/apk/developer/app-developer.apk"
instrumentation="android/app/build/outputs/apk/androidTest/developer/app-developer-androidTest.apk"
test -s "$apk"
test -s "$instrumentation"

adb install -r "$apk"
adb install -r "$instrumentation"
adb shell pm list packages | grep -q 'package:com.michelslab.igcleaner.developer'
mkdir -p artifacts/android-developer

adb shell am instrument -w -r \
  -e class com.michelslab.igcleaner.DeveloperEditionTest \
  com.michelslab.igcleaner.developer.test/androidx.test.runner.AndroidJUnitRunner \
  | tee artifacts/android-developer/instrumentation.txt
grep -Fq 'OK (1 test)' artifacts/android-developer/instrumentation.txt

unzip -p "$apk" assets/ig_cleaner_pro_v120_27_synced_companion.html > /tmp/igc-developer-embedded.html
grep -Fq 'igcDevSaveNote' /tmp/igc-developer-embedded.html
cp "$apk" artifacts/android-developer/app-developer.apk
echo 'PASS: installed Android Developer APK, real Account route, persistent section annotation and native JSON export'
