# GRANADA #14 — Developer auditor private-workspace and AI-export hardening (2026-10-19)

**Issue:** [#162](https://github.com/michels-lab/IG-Cleaner-Pro/issues/162). **Base:** `main` at `cbd8b1ce65d428b6950c71539b2761df5823a907`. **Stage:** integrated into `main` via [PR #163](https://github.com/michels-lab/IG-Cleaner-Pro/pull/163), merge SHA `c949d5dc5147728739a174bbc54f63dfd8c41c1d`, after **6/6 exact-HEAD checks SUCCESS** at `d0a61094e02952c90a580823b675160237f6e1cd`: installed Windows Setup, Desktop contracts/render, Android build/About visual and Supabase RLS. [Issue #162](https://github.com/michels-lab/IG-Cleaner-Pro/issues/162) closed. **Source integrated, not published**.

## Findings
- `run_audit` globbed three action history families within `data_root`, but Python `Path.is_file()` and `read_text()` follow symbolic links. A symlink named like an action journal could cause Developer Edition to examine unrelated local files outside the owner's developer workspace. A symlinked root could redirect the entire scan.
- `ai_prompt(report)` previously included arbitrary caller-supplied `source_revision`, finding descriptions and limitations, and status-count map fields. It claimed a redacted AI prompt while trusting free-form report strings.

## Bounded fix
- Reject symlink `data_root` without traversing it, using fixed `AUDIT_ROOT_IS_SYMLINK` diagnostic.
- Skip linked regular action journals, batch reviews and historical recheck files. Include only the count/fixed-code `EXTERNAL_JOURNAL_LINK_SKIPPED`; no path, target path or filename enters the report. Normal installed read-only diagnostics still process regular files.
- Centralize preapproved finding descriptions/severity in `FINDING_CATALOG`. `ai_prompt` regenerates findings using catalog entries, bounded counts, known status/issue keys, safe release/hash revision metadata and fixed limitations, excluding untrusted arbitrary report/client text.
- Preserve account annotations intentionally authored by the owner in the dedicated Developer UI (which are handled separately); this backend diagnostic-export change does **not** erase, relocate or rewrite those notes.
- Tests extend `tests/test_developer_audit.py` for three symlinked journal variants, symlinked root, unchanged external bytes, safe finding counts, and malicious synthetic report containing a fake username/token/path; no injected content may enter the exported repair prompt.
- Existing Desktop contract and Windows integrated installer workflows already run `tests/test_developer_audit.py`; no shared `ci.yml` change, no overlap with blocked English PR #143.

## Limitations / QA
- Path symlink checks guard the normal app-workspace read path; they do not promise a full OS-level defense against hostile concurrent same-user filesystem races or compromised Windows processes.
- Exact-head CI passed across six jobs, including installed Windows Setup. Those tests do **not** validate real Instagram login, physical Android OTP, browser session recovery or relationship mutation outcomes.
- Official GitHub stable remains **v120.53**, next reserved **v120.54** is **not** published or authorized by this change. Owner tests only official published release installers, never Actions candidate artifacts.

## CI verdict
**SUCCESS (6/6 exact-HEAD checks)** for the merge-candidate commit; owner live account/device acceptance pending. No release created.
