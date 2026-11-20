# GRANADA P0 — Windows slot startup and local bridge cleanup (2026-11-20)

## Source defect and impact (owner issue #377)
The native Windows launcher started the authenticated localhost controller, then called `updater.check()` **outside** its existing `try/finally`. An exception while starting update discovery bypassed `stop_safely(server)`, closed the slot mutex and could leave a daemon bridge/worker running without the intended Chrome UI. A failure in `threading.Thread.start()` likewise left the newly bound listener without `server_close()`. This is a source-path lifecycle gap, **not evidence** that either event has happened on the owner's machine.

## Product correction
- If `serve_forever` thread startup fails, close its bound socket immediately, **without** invoking `shutdown()` (which requires a running serve_forever loop).
- As soon as the controller thread starts, include both optional updater discovery and Chrome launch/wait within one guaranteed `stop_safely(server)` scope.
- If the optional updater fails to *start* its own check, emit only the exception's class name to standard error and continue launching the **already installed** app. No unapproved download or relationship action is initiated.
- If Chrome startup fails, stop action services and close the local server before releasing this slot's named mutex. Preserve the independently running other slot, historic Chrome profiles, protected lists, and WAL.

## Negative source/runtime tests
`tests/test_native_desktop.py` executes actual `main()` startup for **both** `primary` and `secondary` with isolated fake local services, and injects (1) updater failure; (2) Chrome executable failure; (3) listener thread start failure. It asserts correct return codes, exactly one socket closure, updater not blocking usable Chrome, mutex release and no server.shutdown deadlock when the server was never started. The existing Windows integrated-preview workflow runs this test suite.

## Scope and hard boundaries
This is source + mocked offline lifecycle QA. It does **not** establish two physical Windows/Instagram A/B windows, validate the owner's browser-storage quota (#371), fix counter rebound (#360), click Unfollow (#164) or Cancel Pending (#172), or approve v120.81. Global progress remains **6/12 = 50%** until a new existing owner-live or release milestone is demonstrably complete. Official published stable remains **v120.80**; no Developer Edition or preview release is requested.

## Root cause of previously cancelled acceptance (reproduced from GitHub Actions metadata)
Both installer previews for this campaign were **cancelled** by the job's `timeout-minutes: 35`: [Windows #396 run 44828563649](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/44828563649) and [Focus #397 run 44829643695](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/44829643695). The job contains three independent bounded child phases of 600s + 240s + 900s (29 minutes) **after** separately preparing Python, Playwright, Chromium, PyInstaller and native preview builds. When GitHub cancelled it, the installed Windows acceptance was still running and later steps had not executed. Cancellation is **neither PASS nor product failure**.

Raised the **job-level** budget from 35 to 65 minutes, preserving all per-child fail-fast timeouts and every installation/uninstall/security check. CI may now produce a real success or a real bounded failure. This is not an exemption from Windows acceptance and not physical A/B Instagram proof.
