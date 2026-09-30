# Instagram export ZIP fixture

`instagram-export-sample.zip` is a **sanitized fixture derived from the structure of a real Instagram export generated on 2026-09-30**. It contains no real usernames, account IDs, contacts, names, or relationship data.

The fixture deliberately mirrors the reference export at the structural level:

- same 13 archive paths;
- same nested folder layout (`connections/...`);
- same JSON root types and key shapes for every file;
- same three-part Followers split (`followers_1.json`, `followers_2.json`, `followers_3.json`);
- same `label_values` schema used by Pending / Recent / Blocked exports;
- same ZIP storage method used by the reference archive (STORE / method 0).

Expected importer results for this fixture:

- Following: **3**
- Followers: **5**
- Pending: **2**
- Recent follow requests: **1**
- Recently unfollowed: **1**
- Blocked: **1**
- Core ZIP groups: 1 Following file, 3 Followers files, 1 Pending file and 3 supported extra files.

The archive also includes real-world neighboring exports such as `following_hashtags.json`, `close_friends.json`, `removed_suggestions.json`, synced contacts and favorited profiles. Those exist specifically to verify that the importer does **not** misclassify them as Following/Followers/Pending.

Regression validation performed against the 2026-09-30 reference export:
- reference archive: 11,785 Following / 21,824 Followers / 418 Pending;
- sanitized fixture: 3 Following / 5 Followers / 2 Pending;
- both select exactly 1 Following file, 3 Followers files, 1 Pending file and the same 3 supported extras;
- both completed in Chromium without page errors.

Never replace this fixture with a raw personal Instagram export. When Instagram changes its export structure, regenerate a sanitized fixture from the new real structure and update these expectations.
