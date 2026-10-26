# GRANADA v120.65 — verified official FINAL stable publication

**Published:** 2026-10-26T23:09:53Z (October 26, 2026).  
**Official release:** [v120.65](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.65); `draft=false`, `prerelease=false`, **12 assets**.  
**Governed publisher:** [GitHub Actions 40416690593](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/40416690593), `completed/success` (same tagged source; attempt 1).  
**Exact tagged source:** `8570e12836afd3fde966eb8c590c7604aaf224a8` ([release PR #250](https://github.com/michels-lab/IG-Cleaner-Pro/pull/250), functional source [#249](https://github.com/michels-lab/IG-Cleaner-Pro/pull/249)).  
**Previous stable:** [v120.64](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.64), run `40404587656`, tag `593f9d4d0598ea6056bca2247c99e899970ffcb1`.

## Twelve official assets (GitHub-reported SHA-256)

| Release asset | Digest |
| --- | --- |
| `IG-Cleaner-Pro-Android-Developer-v120.65.apk` | `sha256:1bb4e8906f0e571976ef0616ee96121f8dd99bf6d3e1acc401fc74972f06e83a` |
| `IG-Cleaner-Pro-Android-v120.65.apk` | `sha256:f8df5c4a5a861f629f3218d683f984f66d7e928428a25f56992e0241954a0ebd` |
| `IG-Cleaner-Pro-Automatic-Robot-Windows-v120.65.zip` | `sha256:ca2c6d628c336258b4785fbc10b61b43c1156639eeadf36a6595ec3fe180b7bd` |
| `IG-Cleaner-Pro-Desktop-v120.65.html` | `sha256:54caa2ff04c4c7750c220a8e274cf7cfb23d0baa419a3be4aa4629be0e60b766` |
| `IG-Cleaner-Pro-Desktop-v120.65.zip` | `sha256:aa5ce61c2a6e96bad2f05a43c3a482034dd63f69c3759817c57e914744fabb00` |
| `IG-Cleaner-Pro-Windows-Developer-Setup-v120.65.exe` | `sha256:17ecaf76f10de404293c427c8eee01d9936b9afe029237af64fda7a9925cdf7f` |
| `IG-Cleaner-Pro-Windows-Developer-Setup-v120.65.exe.sha256` | `sha256:97a7b927dddd7d5ca5a26649102a2d07ab7b06e8a9fde88f61f2cc785fb44a23` |
| `IG-Cleaner-Pro-Windows-Setup-v120.65.exe` | `sha256:7917943fdd2173ff22ea48cb88826934f2f91d303d89d5bcba0752dcb9b17183` |
| `IG-Cleaner-Pro-Windows-Setup-v120.65.exe.sha256` | `sha256:d6e2f4162cf1f534efd25651e773bfd9efebacbaf7b6d7bce334ca578d2f297e` |
| `Instagram-Cleaner-Pro-v120.65-logo.png` | `sha256:83606858fa1c8ed61a5a76779b4b8330befb185ae3d7c66859c285aa4a67d2ff` |
| `Instagram-Cleaner-Pro-v120.65-PRIVACY.md` | `sha256:f195268d10039308b7972195de452af12fdc29f54341553edcceec76f2a68403` |
| `SHA256SUMS.txt` | `sha256:b808239ff4c77358530ef8d200e9a008283cc918ccaf4928d7f06e5bbb66129d` |

GitHub's official release API exposes these **12** asset digests; the successful governed publisher separately enforced signed Android public/Developer coexistence, installed Windows public/Developer, real rendered UI evidence, checksum files and update-feed validation. This receipt does not claim independent re-download and byte hashing of every published asset by the assistant.

## What is actually fixed

- NEW Windows Unfollow/Cancel action cohorts exclude previously **visited** profile names, not merely profiles where a click was attempted. Durable target navigation reservation precedes `page.goto`; no-click, uncertain and confirmed profiles are all in the scoped visit ledger.
- Exact owner/workspace/task history, protected lists, original saved 10/40 cohorts, click WAL/no-replay, timestamps, existing bookmarks and separate read-only recheck are preserved. The backend rejects stale direct starts and missing/corrupt visit evidence rather than opening Chrome.
- Historical saved-cohort `Continue` for safely never-clicked targets is distinct from NEW batches; no action is auto-approved as Reviewed by this change.
- [PR #249](https://github.com/michels-lab/IG-Cleaner-Pro/pull/249) passed **9/9** exact-head tests; [PR #250](https://github.com/michels-lab/IG-Cleaner-Pro/pull/250) passed exact-head premerge checks. Publisher [40416690593](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/40416690593) then finished **SUCCESS** on tagged merge commit `8570e12836afd3fde966eb8c590c7604aaf224a8`.

## Remaining real-device acceptance and limitations

Owner states installed **v120.64** actually executed Unfollows, but also reopened reviewed profiles across new batches. There is **no validated owner-installed v120.65 new-batch trial** or real Cancel Pending success yet. Keep [#164](https://github.com/michels-lab/IG-Cleaner-Pro/issues/164) and [#172](https://github.com/michels-lab/IG-Cleaner-Pro/issues/172) open for these observations. Repeated own-profile navigation still needs real-device observation [#230](https://github.com/michels-lab/IG-Cleaner-Pro/issues/230). GitHub CI cannot access the user's Instagram session, browser credentials or saved account relationships. Windows Setup has SHA-256 but no Authenticode signature; Android remains outside Google Play.

## Closeout and no accidental republish

One-time `v120.65` authorization is consumed: `authorized=false`, `status=published`, exact `published_run=40416690593`, `published_commit=8570e12836afd3fde966eb8c590c7604aaf224a8`, `published_at=2026-10-26T23:09:53Z`. Manifest and owner-facing README/update/sync guidance advance to `currentStableRelease=v120.65`, `nextRelease=v120.66` **reserved only**, with no fresh authorization. Do not overwrite the immutable `v120.65` tag or re-upload assets. No code, local user history, journal or Chrome profile is changed by this documentation-only closeout.
