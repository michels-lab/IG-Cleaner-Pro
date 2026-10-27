"""Owner-approved, read-only COMPLETE Instagram Followers + Following snapshot.

Separate from Profile Counts/Unfollow/cancel and the imported ZIP workflow.
Runs only inside the local robot Chrome user-data directory. No public service
token, cookie, unfollow operation or credential leaves the browser context.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
import sys
import threading
import time

from profile_actions import _find_verified_owner_tab, _atomic_json, _read_json, PUBLIC_ROBOT_LOGIN_WAIT_SECONDS
from profile_counts_instagram import challenge_detected, preserve_instagram_auth_page
from profile_counts_robot import valid_username
from profile_lists_live import read_live_friendship_list, LiveListsRateLimited
from live_scan_settings import effective_settings, validate_settings, PRESETS, LIMITS
from robot_interlock import ActionLease


class LiveRelationships:
    def __init__(self, collector, actions, data_dir: Path, session_dir: Path):
        self.collector, self.actions = collector, actions
        self.data_dir, self.session_dir = Path(data_dir), Path(session_dir)
        self.lock = threading.RLock()
        self.stop_event = threading.Event()
        self.worker = None
        self.owner = self.account = self.handle = ""
        self.status, self.message = "idle", "No live Instagram verification has started."
        self.pages_completed = 0
        self.members_loaded = {"followers": 0, "following": 0}
        self._session_cooldown_until = 0.0
        self.active_settings = effective_settings(None)

    def _file_for(self, owner, account):
        digest = hashlib.sha256((owner+"\0"+account).encode("utf-8")).hexdigest()[:32]
        return self.data_dir / ("instagram-live-relationships-"+digest+".json")

    def _settings_file(self, owner, account):
        digest = hashlib.sha256((owner+chr(0)+account).encode("utf-8")).hexdigest()[:32]
        return self.data_dir / ("instagram-live-bulk-settings-"+digest+".json")

    def configuration(self, data):
        owner, account = self._scope(data)
        with self.lock:
            if data.get("save") is True:
                if self.worker and self.worker.is_alive():
                    raise ValueError("Stop the running scan before editing timing settings.")
                validated = validate_settings(data.get("settings"))
                _atomic_json(self._settings_file(owner,account), validated)
            elif data.get("save") not in (None, False):
                raise ValueError("Explicit Save required for settings.")
            current = effective_settings(_read_json(self._settings_file(owner,account), {}))
            return {
                "owner":owner,"account":account,
                "settings":current,
                "defaults":dict(PRESETS["recommended"]),
                "presets":{name:dict(values) for name,values in PRESETS.items()},
                "limits":{name:list(bounds) for name,bounds in LIMITS.items()},
                "editable":not bool(self.worker and self.worker.is_alive()),
                "read_only":True,"relationship_action":False,
                "risk_notice":"Conservative app delays, not Instagram quotas; account restrictions remain possible.",
            }

    def _cooldown_file(self, owner, account):
        digest = hashlib.sha256((owner+"\0"+account).encode("utf-8")).hexdigest()[:32]
        return self.data_dir / ("instagram-live-scan-cooldown-"+digest+".json")

    def _global_cooldown_file(self):
        # The same persistent robot Chrome can serve multiple app workspaces.
        # A 429 in one workspace MUST NOT be bypassable by changing account.
        return self.data_dir / "instagram-live-global-cooldown.json"

    def _cooldown_remaining(self, owner, account):
        if not owner or not account:
            return 0
        account_data = _read_json(self._cooldown_file(owner, account), {})
        chrome_data = _read_json(self._global_cooldown_file(), {})
        dates = []
        for item in (account_data, chrome_data):
            if isinstance(item, dict) and item.get("schema") == "igc-bulk-read-cooldown-v1":
                try:
                    dates.append(float(item.get("until",0)))
                except (TypeError, ValueError, OverflowError):
                    continue
        when = max(dates, default=0)
        if (owner, account) == (self.owner, self.account):
            when = max(when, self._session_cooldown_until)
        return max(0, int(when - time.time() + 0.999))

    def _record_cooldown(self, seconds, reason):
        deadline = time.time() + seconds
        self._session_cooldown_until = max(self._session_cooldown_until, deadline)
        record={
            "schema": "igc-bulk-read-cooldown-v1",
            "until": deadline, "reason": reason,
            "no_automatic_retry": True,
        }
        _atomic_json(self._cooldown_file(self.owner, self.account), record)
        # Also stop switching Instagram workspaces to evade a restriction:
        # account and Chrome-wide guardrails both need to expire.
        _atomic_json(self._global_cooldown_file(), record)

    def _scope(self, data):
        owner = str(data.get("owner") or "").strip()
        account = str(data.get("account") or "").strip()
        if not owner or not account or len(owner)>200 or len(account)>120:
            raise ValueError("Select the exact app login and Instagram workspace.")
        return owner, account

    def start(self, data):
        owner, account = self._scope(data)
        handle = valid_username(data.get("expected_handle"))
        if not handle or data.get("expected_handle") != handle:
            raise ValueError("Select an exact Instagram @username to verify.")
        if data.get("read_only_consent") is not True or data.get("confirmation") != "live-relationships:"+handle:
            raise ValueError("Confirm live read-only verification of the exact Instagram owner.")
        remaining = self._cooldown_remaining(owner, account)
        if remaining:
            raise ValueError(
                "Protective Instagram list-scan cooldown: " +
                str((remaining + 59)//60) + " minutes remaining. " +
                "Do not start another scan; existing complete snapshots are preserved.")
        lease = ActionLease(self.data_dir).acquire()
        started = False
        try:
            with self.collector.browser_admission, self.lock:
                if self.worker and self.worker.is_alive():
                    raise ValueError("Live relationship verification is already running.")
                if ((self.actions.worker and self.actions.worker.is_alive()) or
                        (self.collector.worker and self.collector.worker.is_alive())):
                    raise ValueError("Pause all other Instagram Chrome robots before verifying live lists.")
                self.owner,self.account,self.handle=owner,account,handle
                self.pages_completed=0
                self.members_loaded = {"followers": 0, "following": 0}
                self.stop_event.clear()
                self.status, self.message = "starting", "Opening existing robot Chrome for read-only verification."
                self.worker = threading.Thread(target=self._run_with_lease,args=(lease,),daemon=True)
                self.worker.start()
                started=True
                return self._status()
        finally:
            if not started:
                lease.release()

    def _status(self):
        return {"status":self.status,"message":self.message,
                "owner":self.owner,"account":self.account,
                "expected_handle":self.handle,
                "running":bool(self.worker and self.worker.is_alive()),
                "pages_completed":self.pages_completed,
                "members_loaded":dict(self.members_loaded),
                "cooldown_seconds_remaining":self._cooldown_remaining(self.owner,self.account),
                "read_only":True,
                "relationship_action":False}

    def pause(self, data):
        owner,account=self._scope(data)
        with self.lock:
            if (owner,account)!=(self.owner,self.account):
                raise ValueError("Another account owns this live verification.")
            if self.worker and self.worker.is_alive():
                self.stop_event.set()
                self.status,self.message="pausing","Finishing the current read-only page; no partial result will be committed."
            return self._status()

    def results(self,data):
        owner,account=self._scope(data)
        kind=str(data.get("list") or "not_following_back")
        if kind not in ("followers","following","not_following_back","fans"):
            raise ValueError("Choose Followers, Following, not following back, or fans.")
        offset=data.get("offset",0)
        limit=data.get("limit",100)
        if type(offset) is not int or offset<0 or type(limit) is not int or not 1<=limit<=200:
            raise ValueError("List page must have a nonnegative offset and 1–200 profiles.")
        with self.lock:
            if self.worker and self.worker.is_alive() and (owner,account)!=(self.owner,self.account):
                raise ValueError("Another Instagram account is being verified; wait before changing scope.")
            status=self._status() if (owner,account)==(self.owner,self.account) else {
                "status":"idle","message":"No active scan for this account.",
                "owner":owner,"account":account,"read_only":True,"relationship_action":False,
                "running":False,"pages_completed":0}
        saved=_read_json(self._file_for(owner,account),{})
        if not saved:
            return {**status,"complete":False,"captured_at":None,"verified_handle":None,
                    "totals":{},"list":kind,"offset":offset,"usernames":[],"returned":0,
                    "has_next":False,"last_verified":False}
        if (saved.get("schema")!="igc-live-relationships-v1" or
                saved.get("complete") is not True or
                not isinstance(saved.get("lists"),dict)):
            raise ValueError("Stored live relationship evidence is malformed; do not infer non-followback.")
        lists=saved["lists"]
        if any(not isinstance(lists.get(key),list) for key in ("followers","following","not_following_back","fans")):
            raise ValueError("Stored relationship lists are malformed.")
        usernames=lists[kind]
        totals={k:len(lists[k]) for k in ("followers","following","not_following_back","fans")}
        # A completed older snapshot is NOT presented as the current Instagram state.
        return {**status,"complete":bool(status["status"]=="complete" and
                    status.get("expected_handle")==saved.get("expected_handle")),
                "last_verified":True,"captured_at":saved["captured_at"],
                "verified_handle":saved["expected_handle"],"totals":totals,
                "list":kind,"offset":offset,"usernames":usernames[offset:offset+limit],
                "returned":len(usernames[offset:offset+limit]),
                "has_next":offset+limit<len(usernames),"source":"saved_complete_snapshot"}

    def _run_with_lease(self,lease):
        try:
            self._run()
        finally:
            lease.release()

    def _run(self):
        browser=None
        try:
            from playwright.sync_api import sync_playwright
            self.session_dir.mkdir(parents=True,exist_ok=True)
            with sync_playwright() as pw:
                params={"user_data_dir":str(self.session_dir),"headless":False,
                        "viewport":{"width":1180,"height":860}}
                if getattr(sys,"frozen",False):
                    browser=pw.chromium.launch_persistent_context(channel="chrome",**params)
                else:
                    try: browser=pw.chromium.launch_persistent_context(**params)
                    except Exception: browser=pw.chromium.launch_persistent_context(channel="chrome",**params)
                tabs=[p for p in browser.pages if not p.is_closed()]
                page=next((p for p in tabs if preserve_instagram_auth_page(p)),
                          tabs[0] if tabs else browser.new_page())
                if not preserve_instagram_auth_page(page):
                    page.goto("https://www.instagram.com/",wait_until="domcontentloaded",timeout=45000)
                with self.lock:
                    self.status,self.message="login","Sign in as @"+self.handle+" in robot Chrome. Reading only."
                started=time.monotonic()
                while not self.stop_event.is_set():
                    tabs=[p for p in browser.pages if not p.is_closed()]
                    if any(challenge_detected(p) or p.locator('input[name="password"]').count() and
                           p.url.startswith("https://www.instagram.com/challenge") for p in tabs):
                        raise ValueError("Instagram requires manual security verification. No lists were accepted.")
                    verified,mismatch=_find_verified_owner_tab(tabs,self.handle)
                    if mismatch:
                        raise ValueError("Wrong signed-in Instagram account. Expected @"+self.handle+".")
                    if verified:
                        page=verified
                        break
                    if time.monotonic()-started>=PUBLIC_ROBOT_LOGIN_WAIT_SECONDS:
                        raise ValueError("Instagram owner could not be confirmed after manual sign-in.")
                    self.stop_event.wait(2)
                if self.stop_event.is_set():
                    return
                def on_page(kind,index):
                    if self.stop_event.is_set():
                        raise ValueError("Owner paused read-only live verification.")
                    with self.lock:
                        self.pages_completed+=1
                        self.status="running"
                        self.message="Reading current "+kind+" · page "+str(index)+"; no relationship actions."
                def on_progress(kind, count):
                    if self.stop_event.is_set():
                        raise ValueError("Owner stopped the read-only bulk list download.")
                    with self.lock:
                        self.members_loaded[kind] = count
                        self.message = ("Downloading " + kind + " via Instagram list pages: " +
                                        str(count) + " unique accounts loaded, " +
                                        str(self.pages_completed) + " JSON pages. " +
                                        "Not opening individual profiles.")
                def on_rest(kind, index, milliseconds):
                    with self.lock:
                        self.status = "running"
                        self.message = ("Instagram protection: " + str(milliseconds // 1000) +
                                        "s rest after " + str(index) + " bulk " + kind +
                                        " pages; Stop scan works during the pause. " +
                                        "No profile-by-profile visits.")

                def interruptible_wait(milliseconds):
                    if self.stop_event.wait(milliseconds / 1000):
                        raise ValueError("Owner stopped read-only Instagram scan during safety rest.")

                # Bulk JSON pages return member IDs. Compare IDs (not renamable
                # usernames) and only materialize the four visible name lists
                # after BOTH entire streams have verified their terminal cursor.
                # A failure in Following never replaces prior complete snapshots.
                followers=read_live_friendship_list(
                    page,self.handle,"followers",on_page=on_page,
                    on_progress=on_progress,identities=True,
                    on_rest=on_rest,wait_ms=interruptible_wait)
                following=read_live_friendship_list(
                    page,self.handle,"following",on_page=on_page,
                    on_progress=on_progress,identities=True,
                    on_rest=on_rest,wait_ms=interruptible_wait)
                if self.stop_event.is_set():
                    return
                verified,mismatch=_find_verified_owner_tab(
                    [p for p in browser.pages if not p.is_closed()],self.handle)
                if mismatch or verified is None:
                    raise ValueError("Instagram account changed after paging. Snapshot not saved.")
                lists={
                    "followers":sorted(followers.values()),
                    "following":sorted(following.values()),
                    "not_following_back":sorted(
                        following[account_id] for account_id in following.keys()-followers.keys()),
                    "fans":sorted(
                        followers[account_id] for account_id in followers.keys()-following.keys()),
                }
                _atomic_json(self._file_for(self.owner,self.account),{
                    "schema":"igc-live-relationships-v1","complete":True,
                    "matching_method":"stable_account_id_bulk_cursor",
                    "expected_handle":self.handle,"captured_at":time.strftime("%Y-%m-%dT%H:%M:%SZ",time.gmtime()),
                    "lists":lists,"read_only":True})
                # Even successful scans are deliberately not repeatable in a
                # burst. The cooldown is local to this app-login/IG-workspace.
                self._record_cooldown(15*60, "complete")
                with self.lock:
                    self.status="complete"
                    self.message=("Verified BOTH complete Instagram bulk lists by account ID: "+
                        str(len(followers))+" followers, "+str(len(following))+
                        " following. This is an on-demand snapshot, not a continuous feed.")
        except LiveListsRateLimited as exc:
            try:
                self._record_cooldown(exc.wait_seconds, exc.code)
            except Exception:
                # Keep at least the in-memory gate, and never claim a safe
                # persistent cooldown if local storage is unavailable.
                pass
            with self.lock:
                self.status="blocked"
                self.message=("Instagram requested a safety cooldown: " +
                    str((exc.wait_seconds+59)//60) + " minutes minimum. " +
                    "No automatic retries. " + str(exc)[:160] +
                    " Previous saved snapshots are historical only.")
        except Exception as exc:
            with self.lock:
                self.status="paused" if self.stop_event.is_set() else "blocked"
                self.message="Live list verification unavailable: "+str(exc)[:190]+(
                    " Previous saved snapshots are historical only; no incomplete negative results.")
        finally:
            if browser is not None:
                try: browser.close()
                except Exception: pass
            with self.lock:
                if self.stop_event.is_set() and self.status in ("pausing","login","running"):
                    self.status,self.message="paused","Live verification stopped; no partial lists were saved."
