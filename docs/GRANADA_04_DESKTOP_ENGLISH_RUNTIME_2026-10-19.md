# GRANADA #4 — English runtime copy on installed Windows Desktop (2026-10-19)

**Status: implementation candidate; official stable still v120.53; next version v120.54 reserved and not authorized for publication.**

## Scope / boundaries
- Dedicated [issue #142](https://github.com/michels-lab/IG-Cleaner-Pro/issues/142). Independent of integrated Granada #1–#3, parked owner-live Instagram robot #133 and Developer #135.
- Branch `granada/english-runtime-desktop-20261019` based on `main` `6675122fa0d2d3396ff1ba40a15851babb646f8e`.
- Source changed: `desktop/ig_cleaner_pro_v120_27_synced_companion.html` and `tools/ig_cleaner_desktop.py`, plus one focused Python regression suite and CI registration.
- Focus eligible pool, action journals, Instagram relation-click engine, authentication, consent, Windows updater, Developer mode, account scope and public release files **not changed**.

## Changes
- Existing static-English contract allowed numerous owner-facing Spanish runtime strings from the original JS engine.
- Translated **88 selected source fragments / 115 matches** plus five Windows launcher errors, including guided session, Overview/session metrics, recent actions, pace estimates, Focus batch confirmations, evidence precision/diagnostics, critical-priority panels and followers/mutuals summary labels.
- No changes to the literal legacy internal `pendiente` and `vacío` state values, original `Seguidores que sigo` audit-name mapping, persisted keys/IDs or Instagram DOM language-recognition selectors.
- `tests/test_granada_english_runtime.py` enforces representative new English messages, absence of high-traffic old Spanish strings and preservation of historical storage sentinels. Existing `tests/english-ui-contract.py` and runtime Windows Setup smoke remain additional gates.

## Important limitations
- This block updates **the installed Windows/Desktop source**. `index.html` (public web source) and `android/app/src/main/assets/ig_cleaner_workspace.html` (embedded mobile workspace) are larger independent copies and are **not changed** here. End-to-end English parity on Web and Android is still an explicitly parked separate phase; do not misreport cross-platform completion.
- Older Spanish strings and historical codes elsewhere in the Desktop JS may remain. Translate in further independent passes without altering user data or parser locale compatibility.
- Browser-based CSS/DOM language visual QA and owner installed-release acceptance must be independently established; passing source assertions does not prove live Instagram behavior.
- No official release is created by merging this change. Owner tests official releases, never Actions previews.

## Evidence
- Await exact-HEAD CI and Windows installer checks; record exact head / release separately. No privileged cloud mutation or Instagram actions were performed by this branch.
