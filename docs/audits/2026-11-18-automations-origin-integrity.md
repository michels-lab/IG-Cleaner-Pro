# GRANADA — Automations action provenance integrity (2026-11-18)

## Owner requirement and bounded implementation

Issue [#298](https://github.com/michels-lab/IG-Cleaner-Pro/issues/298) requests an Automations activity panel matching Manual Actions' time-window statistics, with separate verified robot actions, legacy unknown-origin records and manual actions. The existing Windows panel already exposed the canonical time windows but had **no usable origin filter**. Thus combined historical values were easy to misread as attributable robot actions despite the backend intentionally preserving `origin=unknown` for old WAL rows.

This source-only branch adds an active provenance selector:
- **Robot y registros históricos** (all saved records, still separating verified from unknown).
- **Solo robot verificado** (only explicit `origin=robot` confirmed results and robot warning events).
- **Origen histórico sin comprobar** (unknown-origin legacy outcomes and warnings, never relabeled successful robot operations).

The origin filter applies to the manual-parity period tiles, per-task breakdown, and saved-history view without loading Instagram or writing/replaying actions. It is per currently selected Windows owner/account and keeps the existing 15-second refresh, independent account selection, collapsible responsive panel, and the rest of Automations.

## Safety and exactness

Apply the provenance filter **after** canonical same-target timestamp reconciliation, never before. Two latest rows with equal timestamp but contradictory provenance/status remain unresolved; hiding `unknown` cannot turn the remaining `robot` copy into an invented success. Keep contradictory history visible as Review in filtered views. Count warning events by their own timestamp and recorded origin, not by the later OK's origin.

These are records in the existing token-protected local action journal; the panel does **not** read or assert cross-device manual-action history. Older entries without recorded origin remain unknown rather than being assigned to manual or robot. No changes to Chrome identities, target visits, action workers, click WAL, protected profiles, localStorage, Supabase, credentials or native Android.

## Regression and acceptance

- Extended `tests/automation-warning-events.test.cjs` with same-timestamp conflicting provenance, robot-only vs historical-unknown OK and warning counts, preservation of unknown warning events on later robot OK, plus a live production UI selector contract.
- Execute `node tests/automation-warning-events.test.cjs` on the exact branch commit through GitHub Actions CI; also require the Windows installed/screenshot gates where applicable. **Do not mark these passed until actual current-SHA runs are verified.**
- Physical installed Windows native activity panel and owner Instagram journal reconciliation remain **OPEN**. Manual+robot combined totals need a trustworthy shared origin boundary rather than guessing about old records. Issue #298 remains open.
- Last officially published stable remains **v120.80**. `v120.81` is only reserved, not authorized; no release/tag/RC/Developer edition or version change on this branch.

## Handoff

Source branch: `granada/automations-origin-integrity-20261118`. Relevant files: `tools/automation_activity_ui.py`, `tests/automation-warning-events.test.cjs`. After PR CI, verify installed Windows screenshots and manual-period parity; continue separate #230 self-profile visit acceptance and P0 #360 owner data tests without changing published v120.80 assets.
