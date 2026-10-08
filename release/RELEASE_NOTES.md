## v120.37 — Correct About composition and permanently visible top-header actions

- Corrected Android and Desktop **About** using Michel's explicit layout: approved Instagram Cleaner Pro + Michel's Lab logos **side by side across the top**, developer identity below, **large unmodified portrait** and one vertical list of Instagram, Facebook, LinkedIn, GitHub and Email with recognizable icons and visible labels.
- Android native Home/Review/Focus/Activity/Profile **About** is now a dedicated always-visible header button. Removed the old adaptive overflow menu in its entirety, including the rejected/nonfunctional **Advanced tools** item and handler. Retained **Sync now** as an explicit adjacent header action.
- Desktop About is fixed in the top app command bar outside the scrolled content/sidebar, with duplicated contextual links and conflicting About CSS removed.
- Android installed-app API 35 emulator Home/About tests validate the actual on-screen controls, measured geometry, official loaded images and all five links at compact and wide sizes; real Chromium smoke validates Desktop top About under scrolling, paired logo geometry, large portrait and social list. Normal regression/build and Supabase RLS tests remain required on exact release commit.
- Desktop and Android use the **same version 120.37**. Production package remains `com.michelslab.igcleaner`, versionCode `12037`, original FINAL-9999 signing identity and same original approved icon. Standalone offline Desktop HTML remains primary; ZIP optional.
- Instagram ZIP import, existing Review/Focus/protection/history, account sync and privacy controls are preserved; no destructive state migrations or new permissions.

**Physical-device acceptance remains separate:** install/update on the user's Samsung, imported authentic ZIP, Focus interactions and production Supabase Desktop↔Android roundtrip cannot be verified by CI. The user's visual review happens after publication, not as a manual blocking approval step.
