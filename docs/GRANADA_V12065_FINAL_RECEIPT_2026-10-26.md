# GRANADA v120.65 — verified official FINAL stable publication

**Published:** 2026-10-26T23:09:53Z. **Official normal release:** [v120.65](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.65), `draft=false`, `prerelease=false`.  
**Governed publisher:** [GitHub Actions run 40416690593](https://github.com/michels-lab/IG-Cleaner-Pro/actions/runs/40416690593), **COMPLETED/SUCCESS** all five stages.  
**Exactly tested and tagged source:** `8570e12836afd3fde966eb8c590c7604aaf224a8`; source change [PR #249](https://github.com/michels-lab/IG-Cleaner-Pro/pull/249) and final release [PR #250](https://github.com/michels-lab/IG-Cleaner-Pro/pull/250) (**10/10 exact-head checks passed before merge**).  
**Previous official stable:** [v120.64](https://github.com/michels-lab/IG-Cleaner-Pro/releases/tag/v120.64), run 40404587656, SHA `593f9d4d0598ea6056bca2247c99e899970ffcb1`.

## Twelve official release artifacts

GitHub release API published exactly twelve assets with their SHA-256 digests. No mutable tag or overwritten assets.

| Released asset | SHA-256 fingerprint |
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

## Release gates passed

- Signed Android public and independent Developer twins with **persistent production certificate**, verified side-by-side installed foreground launch on emulator; per-APK package identity and version 12065. Android real-device owner acceptance remains separate.
- Installed Windows public and Developer Setup built from exact source, launched, sanity checked and safely uninstalled without deleting protected local files; owner-supplied Unfollow reference transport and no-replay action WAL exercised in offline real Chromium.
- Rendered Home/About Desktop and native Android screenshots from exact source, validated canonical identity/asset hashes, standalone self-contained Desktop HTML and official update-feed/SHA256SUMS.
- Functional [PR #249](https://github.com/michels-lab/IG-Cleaner-Pro/pull/249) fixes NEW batch repeats: `visited_usernames` unites every action journal target with a separate durable visit reservation before navigation. Both UI and Windows backend independently exclude previously visited confirmed, uncertain and no-click profiles from NEW cohorts while preserving explicit same saved-cohort Continue. Existing owner/account/task histories, protections, and click-WAL evidence are untouched.
- Windows Setup has SHA-256 integrity but no Authenticode signing. This release is not a beta/RC, Play Store build or silent update.

## Scope & post-publication state

The owner reported Unfollow changes actually succeeded on installed v120.64. This is not proof that every target on v120.65 was successful or that the new no-repeat behavior has been physically confirmed; retain [#164](https://github.com/michels-lab/IG-Cleaner-Pro/issues/164), [#172](https://github.com/michels-lab/IG-Cleaner-Pro/issues/172), [#230](https://github.com/michels-lab/IG-Cleaner-Pro/issues/230) for owner-device acceptance. CI never mutated the owner's Instagram following relationships.

This documentation-only reconciliation consumes one-time v120.65 `authorized=true,status=requested` as `authorized=false,status=published`, corrects `currentStableRelease=v120.65`, reserves `nextRelease=v120.66` **NOT authorized/published**, updates README, sync/migration docs and permanent logs. Preserve published v120.65 tag and checksums; never republish or clobber a previous stable.
