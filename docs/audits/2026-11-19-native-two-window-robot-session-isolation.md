# GRANADA P0 — Independent Windows robot sessions for account slots

Date: 2026-11-19. Branch: `granada/windows-two-slot-robot-session-isolation-20261119`. Related issue: #377; robot priorities #164.

## Root cause

The two native Windows app slots already used distinct `file://` UI documents,
Chrome app `--user-data-dir` paths and named mutexes. However, the native
launcher still constructed both public `Collector` backends with the **same**
`~/.ig-cleaner-pro/instagram-browser` root (and both Developer slots with the
same developer root). The action worker's `ActionChromeProfiles` and manual
`DualChromeSessions` therefore could resolve to the *same persistent
Instagram Chrome profile* even though the *app frontend* was isolated.

Two separate visual windows alone did not satisfy the owner's explicit
two-account session request. This is a browser-session-isolation defect, not
evidence that any unwanted action occurred.

## Production correction

1. Add `instagram_robot_session_path(home, slot)`: the primary remains
   **exactly** `instagram-browser`; secondary uses
   `instagram-browser-secondary` in the corresponding public or Developer
   root. No cookies or credentials are copied, moved, read or deleted.
2. Centralize `window_collector(..., slot, developer=...)` so the **normal
   Windows launch AND installed Setup smoke path** use the identical mapping.
   Both public windows continue to use the original shared
   `profile-counts` canonical action journal (with existing owner/account
   scoping, durable click WAL, global OS lease and history).
3. Keep the legacy manual `account-browser-profiles` for primary, but assign
   the second native slot `account-browser-profiles-secondary` so auxiliary
   read-only/manual Chrome sessions do not cross the independent windows.
   Per-owner/account `ActionChromeProfiles` now derives different directories
   from the slot-specific browser roots without changing its hashing algorithm.
4. Add an offline integrated regression verifying primary old-session marker,
   public/Developer slot separation, same canonical journal root, distinct
   instantiated ActionRobot and manual Chrome root, and absence of an eagerly
   created secondary browser directory. Retain existing native chooser/mutex,
   installer/upgrade and single-window UI tests.

## Boundaries and acceptance

- The **second** window will require its own Instagram sign-in. It cannot
  inherit the first window's cookies. No account switching or relationship
  action is performed by these changes.
- A given Instagram owner+workspace remains protected by its canonical
  click-intent journal and the process-wide lock; second window is not
  permission to run two simultaneous unfollow workers.
- Offline CI can check exact folder wiring and installed executable startup.
  It cannot certify two simultaneous graphical Chrome windows or real
  owner-authorized Unfollow / Cancel Pending behavior. Those remain OPEN
  under #377 and #164 until actual device acceptance.
- This is source-only. Published stable remains v120.80 until governed
  release gates and a separately authorized version pass. Do not call a
  successful CI run a new release.
