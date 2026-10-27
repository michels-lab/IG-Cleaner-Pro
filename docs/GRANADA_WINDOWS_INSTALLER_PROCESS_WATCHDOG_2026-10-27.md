# GRANADA — Bounded Windows Setup and frozen runtime QA (2026-10-27)

## Evidence and scope
- v120.68 governed publisher [run 40499536879](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/40499536879), attempt 1, was cancelled in the native Windows install/launch step, after prior action Chromium, visual QA and Android Developer tests passed. This does NOT prove which child process caused cancellation (external runner cancellation is possible).
- Both public and Developer installer tests had a deceptively named `RunBounded` wrapper that used unlimited `Start-Process -Wait`; the frozen PyInstaller healthcheck also waited indefinitely. This could exhaust the 35-minute job.

## Repair on isolated branch
1. Shared subprocess deadline with per-process Windows tree termination, nonzero exit failure, duration/PID logging, process disposal and explicit bounded 75–150-second installer/healthcheck/smoke/uninstall operations.
2. Governed FINAL and Windows PR preview use the same bounded frozen EXE healthcheck. Both upload any available nonsecret installation logs even when QA fails; preview rebuilds on changed guard sources.
3. Real Windows child-process regression verifies exit 0, exit 7 and forced timeout of a sleeping child. Static contract tests prevent an unbounded helper regression.

## Boundaries
- This does not alter Chrome, Unfollow, Cancel Pending, imported accounts/ZIP, protected users, click-ahead WAL, historical journals, auth, Android, version numbers or release requests.
- Not proof that the previous publisher's cancellation is fixed. CI and installed Windows acceptance required at exact branch head; v120.68 publication attempt 2 stays independent. Do not merge this branch while it is running or misrepresent it as shipped. No RC or new official release.
