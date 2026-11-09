# GRANADA — Show original saved action batches after native Windows restart

## P0 user-visible problem
Two action workers recover their exact owner/account Chrome bindings from disk, but their
in-memory `ActionRobot` snapshot resets to idle on restart. The original 40-person saved
Unfollow/Cancel cohort (possibly reduced to a selected 10-person active subset) still
exists in its canonical WAL, yet the Windows panel reports "sin tarea" and no batch.
This conceals the original size and any unresolved or uncertain click evidence.

## Functional fix
- `DualActionWorkspaces._saved_cohort_summaries` reads **only the exact owner's, account's,
  task's saved original review and action WAL**, using the existing read-only
  `ActionRobot.batch_review` contract; no Playwright, no login/session copy, no target click.
- For each unapproved Unfollow or Cancel Pending cohort, expose **redacted counts only**:
  original and currently selected totals, untouched, actually confirmed actions,
  no-click already-resolved outcomes, Review/ambiguous possible clicks and unavailable
  before click. Do not return target usernames, session paths, cookies or tokens.
- If original WAL is invalid, show `unverifiable` rather than pretending there is
  nothing to resume. Never auto-resume a worker, grant parallel consent, or classify
  an uncertain click as OK.
- The native Windows panel visibly distinguishes "**TANDA GUARDADA
  (no ejecutándose)** · Original 40 · Selección actual 10 · Sin registro 7 ·
  Review/advertencias 1" per Instagram account.
- Tests exercise the actual Python controller after cold restart and the actual
  Chromium-rendered dual-panel UI. Fixtures include two accounts, 40→10, an
  interrupted click, previous no-click outcome, corrupted history, byte-for-byte
  journal preservation and no restarted action/browser.

## Still pending
Owner real-session Instagram Unfollow/Cancel Pending acceptance and original
ZIP comparison; synthetic offline tests do not establish those outcomes.
Hard release hold remains: NO RC, tag, APK, Setup, release or version bump.
