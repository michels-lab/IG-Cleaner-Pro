## v120.40 — Safe multi-Instagram profile recovery (Desktop + Android)

- **Fix “Datos anteriores” on Android:** the native account selector now displays selectable Instagram rows rather than only action buttons; the original pre-v120.39 lists and reviews remain in the protected `legacy` workspace.
- **Fix “duplicate value” without deleting history:** explicitly reassign an @username previously assigned to a mistakenly created workspace back to Datos anteriores. Only the displayed handle changes; the other workspace remains accessible as “Sin asignar”, with its original lists, reviews, Focus, Double Check and audits untouched. Cross-device stale edits are rejected.
- **Smart profile creation:** choose between associating an @username with the original history or creating a genuinely separate, empty Instagram workspace. Existing handles cannot accidentally generate duplicate profiles.
- **Rename Instagram handles** in Desktop and Android independently of immutable account keys or state.
- **Per-profile insights** in Desktop selector and native Android Profile: Following, Followers, Pending, review counts and last synchronized list snapshot, reported by the owner-scoped Supabase query.
- **Safely remove named Instagram workspaces** with typed confirmation; the protected original cannot be removed using this control. Formerly assigned/now-unnamed workspaces also support deletion.
- **Export an individual cloud backup** for the selected Instagram, also offered before optional deletion. Exports include synchronized records only, not original local Instagram ZIPs or unsynced local records. The JSON is a backup artifact, not a one-click restore feature.
- **Security:** atomically scoped deletion and metadata-only identity transfer, RLS-owner isolation, least-privilege callable functions and 99 pgTAP assertions. Production Supabase migrations were deployed in advance without changing any customer's identity or historical records.
- **Shipping contract:** v120.40 Android production-signed APK and Desktop standalone/offline HTML (plus optional ZIP), with common release tag; Android package `com.michelslab.igcleaner`, versionCode `12040` and original production certificate. Automated release validations are required; no human visual approval gate.

**Still pending after publication:** genuine Samsung device/update acceptance, real Instagram ZIP parsing and authenticated multi-profile Android↔Desktop roundtrip tracked in [issue #24](https://github.com/michels-lab/IG-Cleaner-Pro/issues/24). No Google Play listing is asserted.
