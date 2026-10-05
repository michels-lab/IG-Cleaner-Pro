# IG Cleaner Pro — Infrastructure & Privacy Audit

Last reviewed: **2026-10-05**

## Current architecture
- **Local-first browser tool.**
- Instagram export ZIP/JSON/HTML files are parsed locally.
- No backend is required for the primary workflow.
- No Instagram login/API automation is required.
- Raw Instagram export data are not uploaded to a server by the current design.

## Why no cloud backend is currently the correct architecture
The app handles highly personal relationship/export data. Its current privacy advantage is that the files remain on the user's machine. Adding Supabase, Google Drive, or another backend by default would materially change that privacy model and is therefore not a neutral implementation detail.

## Gaps / required follow-up
1. Add repository CI for deterministic browser/import regression tests.
2. Define a safe distribution/update architecture for the single-file/local-app model.
3. Move About/developer markup toward the shared Michel's Lab component contract.
4. Add a centralized privacy surface explaining local processing, persisted browser state, exports and any future network feature.
5. Keep sanitized fixtures in Git; never commit real Instagram exports.
6. Document browser-storage schema/version migration so local review history survives app upgrades.

## Optional cloud-sync boundary
If the product later gains opt-in cross-device sync, default scope should be **review metadata/settings**, not the raw Instagram export.

Before enabling any Supabase-backed sync:
- explicit opt-in;
- user authentication;
- RLS on every exposed table;
- `user_id` ownership on every user row;
- publishable key only in the browser;
- secret/service-role key only in trusted server/Edge Function code;
- clear delete/export controls;
- documented retention;
- migration/version field for stored review state;
- tests proving one user cannot read another user's rows.

Raw Instagram ZIP contents should remain local unless the user explicitly chooses a separate upload/backup feature.

## Secret rule
This app currently needs no end-user cloud secret. If a future backend is added, no privileged key may be embedded in `index.html`.
