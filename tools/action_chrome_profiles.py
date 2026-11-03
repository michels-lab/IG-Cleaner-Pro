"""Isolated persistent Chrome profiles for each app owner / Instagram account.

Legacy Windows robots historically shared ONE persistent Chrome user-data-dir
while their action WAL was already owner/account-scoped. Changing the selected
workspace could therefore leave Chrome signed in as the preceding Instagram
account. Never copy or move the legacy login cookies to an arbitrary account.
Each scope signs in manually once, retaining its own persistent browser data.

This module only computes a private local path. It never launches Chrome,
reads credentials, changes a relationship or alters the action journal.
"""
from __future__ import annotations

import hashlib
from pathlib import Path


class ActionChromeProfiles:
    def __init__(self, legacy_session_dir):
        self.legacy_session_dir = Path(legacy_session_dir).resolve()
        self.root = (self.legacy_session_dir.parent /
                     (self.legacy_session_dir.name + "-account-action-chrome-v1"))

    def directory(self, owner, account):
        if (not isinstance(owner, str) or not isinstance(account, str)
                or not owner or not account or len(owner) > 200
                or len(account) > 120
                or any(ord(ch) < 32 for ch in owner + account)):
            raise ValueError("Choose a valid app owner and Instagram workspace.")
        digest = hashlib.sha256((owner + "\0" + account).encode("utf-8")).hexdigest()[:32]
        return self.root / digest
