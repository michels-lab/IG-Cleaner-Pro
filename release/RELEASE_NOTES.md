## v120.36 — Android About visibility and release quality

- Fixed the native Android About regression where the author and Michel's Lab content were hidden by zero-width stacked identity panels.
- Redesigned compact About to show both identities, the **TOOLS WITH IDENTITY.** slogan, and all five social/contact links together without scrolling. Kept the existing official app mark pending the separately approved high-resolution replacement asset.
- Added an installed-APK Android emulator test at compact/wide resolutions. It verifies actual measured image/view dimensions, fully visible contact links on opening, and archives six real screenshots bound to candidate SHA and APK digest.
- Introduced mandatory automated rendered-UI validation before a governed stable release; no manual approval queue is required because the user reviews released builds afterward.
- Updated Android and Desktop development version to **120.36**; kept the production package `com.michelslab.igcleaner` and existing FINAL-9999 signing certificate unchanged.
- Existing local-first data preservation, Focus/state migration and Supabase RLS behavior remain unchanged; real-phone upgrade, Instagram ZIP and cloud sync acceptance stay tracked separately.

**Release status:** development candidate only. Do not claim v120.36 is already published. The user-selected new app logo remains pending exact original PNG import and platform migration.
