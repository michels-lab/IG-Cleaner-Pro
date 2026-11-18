# IG Cleaner Pro · Granada — Automations journal reconciliation (2026-11-17)

## Issue and root cause

Tracking: [Automations activity #298](https://github.com/michels-lab/IG-Cleaner-Pro/issues/298). The read-only Windows Automations panel grouped records using `task + lowercased Instagram username`, but `summarize()` selected the **first** encountered row. Older persistent journals may contain case variants of one handle in distinct JSON keys. JSON insertion order is not proof of chronology: an earlier Review could hide a more recent robot-verified OK; the reverse ordering could show an obsolete OK instead of a newer Review. The historical 2026-11-09 warning-counter test repeated an **identical row**, so it did not detect different outcomes for case variants.

## Implementation

- Source: `tools/automation_activity_ui.py`, shared pure `reconciledOutcomes` used by both `summarize` and `renderHistory`. Group per task and casefolded handle; select the **latest valid UTC timestamp** regardless of saved insertion order. The visible last-15 journal and period counters now agree on contradictions.
- Keep Review/error/blocked events from every duplicate record, deduplicated by scoped handle + status + exact event timestamp. Display them in their actual rolling/calendar time windows, even after a newer verified success.
- Fail closed on conflicting statuses/provenance at identical latest timestamps: never count a verified click or manufacture legacy provenance. Newer Review supersedes older OK in the current result.
- Do not open Instagram, create a robot, edit journals, delete local history, change account selection or modify the release pipeline.

## Regression

The existing production-function Node VM test `tests/automation-warning-events.test.cjs` now covers timeline parity and both JSON row orders, repeated snapshots, distinct warning times, newer Review superseding OK, equal-time origin conflict and independent Unfollow/Cancel tasks for the same handle. The test is already a required step in Linux CI and installed Windows preview workflow; no additional runtime permissions.

## Evidence and limits

**Source branch:** `granada/automation-history-casefold-reconciliation-20261117`, [PR #372](https://github.com/michels-lab/IG-Cleaner-Pro/pull/372). Production pure functions were executed in the isolated JS engine against case-variant negative fixtures, warning deduplication and conflicting proof: PASS. The committed Node VM test and CI/Chromium/installed Windows evidence must still pass at the **exact final SHA** before merge. No browser screenshots or installed-Windows claims are made.

**Published stable at start:** [v120.78](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.78). A separate [v120.79 governed publisher](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/44204338029) was in progress on earlier source when this branch began; do not change its tag/artifacts or claim this code is in that release.

**Still open:** real owner signed-in Windows verification, true legacy manual/robot combined origin, Focus counter rebound #360, actual two-Instagram profile isolation and all other critical physical acceptance. Issue #298 remains open until corresponding runtime and owner acceptance. Release hold/one-time authorization are unchanged.
