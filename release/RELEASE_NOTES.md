## v120.36 — About fix, new logo and real visual QA

- Rebuilt the native Android About view: corrected invisible zero-width panels and made Michel Duarte, Michel's Lab, **TOOLS WITH IDENTITY.** and all five social buttons visible on compact phones without scrolling.
- Replaced the old stacked-layers product logo with the user's approved first concept: overlapping contact cards, cyan orbit and gold sparkle. Preserved the unmodified **1254×1254 PNG** in both master and child repositories (SHA-256 `f913686282731c0a076ec6167989ca05c60c25cea18d51e964343f444284d7a8`).
- Integrated lossless launcher sizes, Android toolbar/About/splash/workspace imagery, Desktop favicon/rail/About icon, and production ZIP/release PNG artwork. The original official Michel's Lab branding and source portrait remain unchanged.
- Android UI instrumentation now launches the installed debug APK and captures **Home and About at compact and wide screen sizes**; captures are bound to source SHA, APK digest and actual PNG bytes.
- Desktop Chromium UI tests launch the distributable HTML, open/close About, validate portrait/studio logo and social links, and capture **six Home/About images** at compact/wide sizes.
- The governed stable publisher now requires successful, same-commit Android and Desktop real rendered UI screenshot evidence before publishing, without a manual pre-release approval queue. The user reviews the release afterward.
- Android and Desktop application identity updated to **v120.36**, keeping production Android package `com.michelslab.igcleaner` and the same FINAL-9999 signing certificate.
- Preserves local Instagram ZIP import and review/Focus/state migration logic, account cloud privacy/delete controls and seven-table Supabase RLS isolation; fixture, contractual and database automated tests still run.

**Boundaries:** Android emulator and Desktop automated tests are NOT a physical-Samsung update-path, real Instagram export, real Supabase account connectivity or Google Play acceptance test; that remains separately documented. The release publisher must report actual GitHub success before claiming v120.36 is published.
