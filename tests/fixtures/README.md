# Synthetic Instagram export fixture

This fixture is intentionally synthetic. It contains no real Instagram account data and exists only to regression-test IG Cleaner Pro's complete-ZIP import workflow.

File: `instagram-export-sample.zip`

Expected archive structure includes:
- `following.json`
- multiple `followers_*.json` files
- `pending_follow_requests.json`
- `recent_follow_requests.json`
- `recently_unfollowed_profiles.json`
- `blocked_profiles.json`
- an unrelated file that the importer should ignore

Expected synthetic usernames include `follow_a`, `mutual_b`, `fan_c`, `fan_d`, `pending_e`, `recent_f`, `unfollow_g`, and `blocked_h`.

Use this fixture whenever the ZIP importer, automatic category detection, recursive archive scanning, multi-file Followers merge, or Pending import is changed. Never replace it with a real user export.
