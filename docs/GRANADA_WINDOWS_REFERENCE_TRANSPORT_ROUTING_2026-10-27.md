# GRANADA — Windows reference Unfollow routing regression (2026-10-27)

## Root cause and reproduction

- Candidate: [v120.68 PR #262](https://github.com/michels-lab/IG-Cleaner-Pro/pull/262). Official stable remains v120.67.
- [Windows integrated CI run 40493835174](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/40493835174) failed 3/6 offline Chromium reference Unfollow scenarios on exact parent SHA d97eb522c1d2557605c7a537ed0674c79b7c2f29.
- PR #262 changed perform_visible_action(use_reference_transport=True) to False. The real ActionRobot._run() did not pass the flag, silently selecting the legacy visible Following/menu click route instead of the owner-approved exact-following-ID lookup and one-shot GraphQL Unfollow.
- Test gap: isolated reference-function tests proved the transport itself but did not pin the production Windows worker routing; the Chromium fixture caught the divergence without touching Instagram.

## Source repair in isolated child branch

1. Restore default reference transport for WAL-backed Unfollow call sites; explicitly pass use_reference_transport=(self.task == 'unfollow') in the actual worker. Cancel Pending retains visible Requested control, not invented GraphQL cancel.
2. Add AST-backed tests validating the real worker routing, same exact transport safety gate and durable pre-click WAL. Existing real Chromium E2E keeps expecting the single reference lookup/POST, not weakened to the legacy path.
3. Add local intercepted Chromium negative fixture: accepted mutation response but still-Following on fresh exact-target page must yield pending Review, never OK, with just one POST and one WAL. No automatic second mutation.

## Validation and limitations

- The child change is source/fixture submitted to CI, NOT merged into parent or published yet. Wait for exact child SHA Windows installed/Chromium and other required checks; then merge child into candidate and repeat exact parent-head required QA.
- No new release is authorized merely by source changes. Production release requires Windows public+Developer installers, Android public+Developer/signing, authentic visual evidence, checksum/update feed and independent FINAL publisher (never RC).
- Neither these fixtures nor CI interact with owner Chrome, cookies, saved 40-person batch, protected profiles, actual Instagram relationship actions, or Android private data.
- Actual signed-in owner Unfollow/Cancel Pending acceptance remains OPEN in #164/#172. Keep exact statuses: submitted, CI passed, merged, published, owner-validated are different.
