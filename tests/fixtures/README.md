# Sanitized Instagram export fixture

The directory `instagram-export-sample/` is an auditable, sanitized structural fixture based on the shape of a real Instagram export. It contains no real usernames, account IDs, contacts, names, or relationship data.

The previous binary ZIP fixture was removed after CI proved that the committed archive was corrupt. Keeping the fixture unpacked makes every regression input reviewable in Git while preserving the same logical export layout.

The fixture intentionally contains 13 files under `connections/...`, including:
- one Following JSON file;
- three Followers JSON parts;
- one Pending follow requests JSON file;
- recent follow requests HTML;
- recently unfollowed and blocked JSON;
- neighboring exports that must not be misclassified as Following/Followers/Pending.

Expected core counts:
- Following: **3**
- Followers: **5**
- Pending: **2**
- Followers parts: **3**
- Total fixture files: **13**

CI validates that every JSON document parses fully, the HTML fixture is valid UTF-8 and references Instagram, and the expected relationship groups/counts remain intact.

Never replace this fixture with a raw personal Instagram export. If Instagram changes its export structure, regenerate sanitized text fixtures from the new shape and update the explicit expectations.
