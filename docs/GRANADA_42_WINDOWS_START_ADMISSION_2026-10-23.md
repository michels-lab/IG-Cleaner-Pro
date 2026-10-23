# GRANADA #42 — Windows Run admission and visible refusal, 2026-10-23

## Owner reproduction and concrete source fault
The installed official v120.58 screenshot has a saved unapproved ten-target cohort (two unresolved, eight untouched), yet the action worker shows 0/0 and the top banner says "Queue prepared". The owner reports Run makes no change. The existing Desktop handler catches local HTTP rejections and writes them to `igcAutoStatus`; ordinary `igcAutoRender`/background polls can replace that with a generic queue sentence. This masks the true blocker and makes a rejected start look inert. Screenshot alone does not establish why the particular Windows request was refused.

## Functional repair, not a claimed Instagram success
- Run now reports a visible, persistent **Checking → Approval → Starting → Accepted / Blocked** command outcome. It displays whether no start was sent, consent was cancelled, the cohort size conflicts, the local backend rejected start, or the backend's returned identity/task/status is wrong.
- A JSON HTTP 200 does **not** count as start success: local start must return the requested owner, account, task and a genuinely active worker. Preserve a rejected explanation across every background status poll. Guard duplicate Start clicks while an admission is pending, without automating any new clicks.
- Keep owner confirmation, exact saved cohort and protected-target logic unchanged. Browser admission trace never exposes session tokens, raw passwords, private profile data or makes a live Instagram request.
- New Node VM test uses the actual Desktop command script and simulates a denied local backend, status polls and a nominal HTTP 200 with no worker; assert refusal stays visible and no success is claimed.
- This does **not yet solve** a missing Instagram Following control in the owner's session. Real installed v120.58 user acceptance on Windows remains OPEN (#172/#164). No RC, prerelease or release until exact-head tests and physical acceptance. No unrelated repositories changed.
