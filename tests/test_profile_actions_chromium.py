"""Real Chromium DOM tests against offline Instagram-like pages.

All www.instagram.com navigation is intercepted locally: never log into or
change a real account. These tests exercise actual Playwright selectors/clicks.
"""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from profile_actions import perform_visible_action, classify_followback_search, perform_visible_followback_audit
from profile_counts_instagram import signed_in_handle, read_following_visible, FollowingControlUnavailable

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None


def fake_profile(locale="en", private=False, account="my.profile", result="follow",
                 blocked=False, request_unfollow=False, warning_handle="target.user",
                 include_warning=True):
    following, unfollow, follow = (("Siguiendo", "Dejar de seguir", "Seguir")
                                   if locale == "es" else
                                   ("Following", "Unfollow", "Follow"))
    requested, cancel = (("Solicitado", "Cancelar solicitud")
                         if locale == "es" else ("Requested", "Cancel Request"))
    warning = ((f"If you change your mind, you'll have to request to follow @{warning_handle} again."
                if locale == "en" else
                f"Si cambias de opinión, tendrás que enviar otra solicitud para volver a seguir a @{warning_handle}.")
               if include_warning else
               f"Are you sure you want to stop following @{warning_handle}?")
    # One button in the target header and a DIV action row like Instagram's
    # visually rendered Following popup. A private profile adds a second dialog.
    return f"""<!doctype html><html lang="{locale}"><head><meta charset="utf-8"></head><body>
    <nav><a href="/{account}/" aria-label="Profile">Profile</a></nav>
    <header>
      <h1>target.user</h1>
      <button id="relationship" onclick="openRelationship()">{following}</button>
    </header>
    <div id="action-menu" role="dialog" style="display:none">
      <div>Add to close friends list</div>
      <div>Add to favorites</div>
      <div>Mute</div>
      <div>Restrict</div>
      <div id="unfollow" onclick="chooseUnfollow()">{unfollow}</div>
      <button id="cancel-request" onclick="finishChange()" style="display:none">{cancel}</button>
    </div>
    <div id="request-confirm" role="dialog" style="display:none">
      <p>{warning}</p>
      <button id="request-unfollow" onclick="finishChange()">{unfollow}</button>
      <button id="request-dismiss" onclick="dismissRequest()">{'Cancelar' if locale == 'es' else 'Cancel'}</button>
    </div>
    <div id="private-confirm" role="dialog" style="display:none">
      <button id="private-confirm-action" onclick="finishChange()">{unfollow}</button>
    </div>
    <script>
     const label={follow!r}, privateFlow={str(private).lower()},
           blocked={str(blocked).lower()}, result={result!r},
           requestUnfollow={str(request_unfollow).lower()};
     window.__steps=[];
     function openRelationship() {{
       window.__steps.push('open');
       if(requestUnfollow) {{
         document.querySelector('#request-confirm').style.display='block';
         return;
       }}
       document.querySelector('#action-menu').style.display='block';
       if(document.querySelector('#relationship').textContent.includes('Solicitado') ||
          document.querySelector('#relationship').textContent.includes('Requested')) {{
         document.querySelector('#unfollow').style.display='none';
         document.querySelector('#cancel-request').style.display='block';
       }}
     }}
     function chooseUnfollow() {{
       window.__steps.push('unfollow');
       document.querySelector('#action-menu').style.display='none';
       if(privateFlow)document.querySelector('#private-confirm').style.display='block';
       else finishChange();
     }}
     function dismissRequest() {{
       window.__steps.push('dismiss');
       document.querySelector('#request-confirm').style.display='none';
     }}
     function finishChange() {{
       window.__steps.push('confirmed');
       document.querySelector('#action-menu').style.display='none';
       document.querySelector('#private-confirm').style.display='none';
       document.querySelector('#request-confirm').style.display='none';
       if(result==='follow')document.querySelector('#relationship').textContent=label;
       if(result==='followback')document.querySelector('#relationship').textContent=
         document.documentElement.lang==='es'?'Seguir también':'Follow Back';
       if(blocked)document.body.insertAdjacentHTML('beforeend','<span>Try again later</span>');
     }}
    </script>
    </body></html>"""



class FollowbackAuditClassifierTests(unittest.TestCase):
    def test_verified_positive_negative_and_inconclusive_are_disjoint(self):
        self.assertEqual(classify_followback_search(None,"target.user",text="",usernames=["target.user"]),"follows_you")
        self.assertEqual(classify_followback_search(None,"target.user",text="No results found",usernames=[]),"not_following")
        self.assertEqual(classify_followback_search(None,"target.user",text="",usernames=[]),"unverified")
        self.assertEqual(classify_followback_search(None,"target.user",text="No results found",usernames=["other.user"]),"unverified")


class RealBrowserSelectorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if sync_playwright is None:
            raise unittest.SkipTest("Python Playwright is not available.")
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch(headless=True)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.pw.stop()

    def setUp(self):
        self.context = self.browser.new_context()
        self.page = self.context.new_page()

    def tearDown(self):
        self.context.close()

    def test_home_owner_switcher_identifies_session_not_suggested_users(self):
        # Mimics a real Desktop Home with collapsed icon-only Profile navigation.
        # Positive proof is only the own-account row immediately next to Switch.
        self.page.set_content("""<!doctype html><html><body>
          <nav><a href="/explore/">Explore</a></nav>
          <main><a href="/someone.else/">Feed post author</a></main>
          <aside style="position:absolute;top:40px;right:20px;width:360px">
            <section style="display:flex;height:70px;width:330px">
              <a href="/realmichelduarte/">realmichelduarte</a>
              <div role="button">Switch</div>
            </section>
            <strong>Suggested for you</strong>
            <a href="/not.me/">not.me</a>
          </aside></body></html>""")
        self.assertEqual(signed_in_handle(self.page), "realmichelduarte")
        self.page.locator("aside").evaluate("""aside => aside.insertAdjacentHTML(
          'beforeend',
          '<section style="display:flex;height:70px;width:330px"><a href="/another/">another</a><button>Switch</button></section>'
        )""")
        self.assertIsNone(signed_in_handle(self.page))



    def following_fixture(self, control="button", opened=False, language="en"):
        label = ("1 seguidos" if language == "es" else "1 following")
        if control == "button":
            button = f'<button id="following-control" onclick="openList()">{label}</button>'
        elif control == "link":
            button = (f'<a id="following-control" href="/realmichelduarte/following/" '
                      f'onclick="openList();return false;">{label}</a>')
        elif control == "text":
            button = f'<div onclick="openList()"><span>{label}</span></div>'
        else:
            button = '<button id="followers-only" onclick="window.badClicks++">5 followers</button>'
        html = f"""<!doctype html><html><body>
          <nav><a href="/realmichelduarte/" aria-label="Profile">Profile</a></nav>
          <header><h2>realmichelduarte</h2><button>Edit profile</button>{button}</header>
          <div role="dialog" id="following-dialog" style="display:{'block' if opened else 'none'}">
            <h2>Following</h2><a href="/friend.user/">friend.user</a>
          </div>
          <script>window.badClicks=0;window.openCount=0;
          function openList() {{ window.openCount++;document.querySelector('#following-dialog').style.display='block'; }}
          </script></body></html>"""
        self.page.route("https://www.instagram.com/**",
                        lambda route: route.fulfill(status=200, content_type="text/html", body=html))

    def test_following_collection_accepts_header_button_or_link(self):
        for control in ("button", "link", "text"):
            with self.subTest(control=control):
                self.page.unroute_all()
                self.following_fixture(control=control)
                usernames, complete = read_following_visible(
                    self.page, "realmichelduarte", max_scrolls=9)
                self.assertEqual(usernames, ["friend.user"])
                self.assertTrue(complete)
                self.assertEqual(self.page.evaluate("window.openCount"), 1)

    def test_following_collection_accepts_owner_opened_dialog(self):
        self.following_fixture(control="none", opened=True)
        usernames, complete = read_following_visible(
            self.page, "realmichelduarte", max_scrolls=9)
        self.assertEqual(usernames, ["friend.user"])
        self.assertFalse(complete)
        self.assertEqual(self.page.evaluate("window.badClicks"), 0)

    def test_missing_following_never_clicks_followers(self):
        self.following_fixture(control="none", opened=False)
        with self.assertRaises(FollowingControlUnavailable):
            read_following_visible(self.page, "realmichelduarte", max_scrolls=3)
        self.assertEqual(self.page.evaluate("window.badClicks"), 0)

    def test_spanish_following_button(self):
        self.following_fixture(control="button", language="es")
        usernames, complete = read_following_visible(
            self.page, "realmichelduarte", max_scrolls=9)
        self.assertEqual(usernames, ["friend.user"])
        self.assertTrue(complete)

    def attempt(self, *, task="unfollow", locale="en", private=False,
                account="my.profile", result="follow", protected=False, blocked=False,
                request_unfollow=False, warning_handle="target.user", include_warning=True,
                pending_already_following=False, missing_profile=False):
        html = fake_profile(locale=locale, private=private, account=account,
                            result=result, blocked=blocked,
                            request_unfollow=request_unfollow,
                            warning_handle=warning_handle,
                            include_warning=include_warning)
        # Intercept all Instagram URLs, even accidental external navigations.
        self.page.route("https://www.instagram.com/**",
                        lambda route: route.fulfill(status=200, content_type="text/html", body=html))
        if task == "cancel" and not pending_already_following and not missing_profile:
            self.page.add_init_script("""document.addEventListener('DOMContentLoaded',()=>{
                document.querySelector('#relationship').textContent =
                    document.documentElement.lang==='es'?'Solicitado':'Requested';
            });""")
        if missing_profile:
            self.page.add_init_script("""document.addEventListener('DOMContentLoaded',()=>{
                document.querySelector('#relationship').textContent = 'Unknown status';
            });""")
        status, message = perform_visible_action(
            self.page, "target.user", task, "my.profile",
            (lambda _: not protected))
        return status, message, self.page.evaluate("window.__steps")


    def test_read_only_audit_searches_own_followers_without_relation_click(self):
        for follows in (True, False):
            with self.subTest(follows=follows):
                html = """<!doctype html><html><body>
                <nav><a href="/my.profile/" aria-label="Profile">Profile</a></nav>
                <a href="/my.profile/followers/" onclick="showFollowers(event)">123 followers</a>
                <div role="dialog" id="dialog" style="display:none">
                  <input placeholder="Search" oninput="searchUsers(this.value)">
                  <div id="results"></div>
                </div>
                <button id="danger" onclick="window.__dangerous.push('follow')">Following</button>
                <script>
                window.__dangerous=[];
                function showFollowers(event) { event.preventDefault();document.querySelector('#dialog').style.display='block';}
                function searchUsers(value) {
                  document.querySelector('#results').innerHTML =
                    value.toLowerCase()==='target.user'&&window.__follows
                      ? '<a href="/target.user/">target.user</a>' : 'No results found';
                }
                </script></body></html>"""
                # Loaded as offline response even though the URL looks like Instagram.
                self.page.route("https://www.instagram.com/**",
                    lambda route: route.fulfill(status=200,content_type="text/html",body=html))
                self.page.goto("https://www.instagram.com/")
                self.page.evaluate("(f) => window.__follows=f", follows)
                # The mocked page reloads on audit navigation; persist fixture flag.
                self.page.add_init_script("window.__follows = " + ("true;" if follows else "false;"))
                status, relation, details = perform_visible_followback_audit(
                    self.page, "target.user", "my.profile")
                self.assertEqual((status,relation),("ok","follows_you" if follows else "not_following"),details)
                self.assertEqual(self.page.evaluate("window.__dangerous"),[])
                self.page.unroute_all()


    def test_login_detects_editable_owner_profile_without_profile_nav(self):
        from profile_counts_instagram import signed_in_handle
        html = """<!doctype html><html><body>
          <header><h2>my.profile</h2><button>Edit profile</button></header>
          <main><a href="/random.person/">Random public profile</a></main>
        </body></html>"""
        self.page.route("https://www.instagram.com/**",
            lambda route: route.fulfill(status=200, content_type="text/html", body=html))
        self.page.goto("https://www.instagram.com/my.profile/")
        self.assertEqual(signed_in_handle(self.page), "my.profile")
        self.page.goto("https://www.instagram.com/somebody.else/")
        self.assertIsNone(signed_in_handle(self.page),
            "A profile URL must never prove the active account without matching owner controls")
        self.page.unroute_all()


    def _collapsed_profile_nav_attempt(self, *, task="cancel", proven_owner="my.profile",
                                       misleading_nav=False):
        """Other-user profile has no semantic Profile link, like owner screenshot."""
        target = fake_profile(account="my.profile", request_unfollow=(task == "cancel"))
        target = target.replace(
            '<nav><a href="/my.profile/" aria-label="Profile">Profile</a></nav>',
            ('<nav><a href="/someone.else/" aria-label="Profile">Profile</a></nav>'
             if misleading_nav else
             '<nav><button aria-label="Profile">☻</button></nav>')
        if task == "cancel":
            target = target.replace('document.querySelector("#relationship")', 'document.querySelector("#relationship")')
            target = target.replace(
                '<button id="relationship" onclick="openRelationship()">Following</button>',
                '<button id="relationship" onclick="openRelationship()">Requested</button>')
        owner = (f'<html><body><header><h2>{proven_owner}</h2>'
                 '<button>Edit profile</button></header></body></html>')
        visits = []
        def route(request):
            uri = request.request.url
            visits.append(uri)
            html = owner if uri.rstrip("/").endswith("/my.profile") else target
            request.fulfill(status=200, content_type="text/html", body=html)
        self.page.route("https://www.instagram.com/**", route)
        status, message = perform_visible_action(self.page, "target.user", task,
                                                  "my.profile", lambda _: True)
        return status, message, self.page.evaluate("window.__steps"), visits

    def test_cancel_pending_with_collapsed_profile_sidebar_verified_via_readonly_tab(self):
        status, message, events, visits = self._collapsed_profile_nav_attempt()
        self.assertEqual(status, "ok", message)
        self.assertEqual(events, ["open", "confirmed"])
        self.assertTrue(any("/my.profile/" in u for u in visits),
                        "A read-only own-profile proof must be checked")

    def test_unfollow_with_collapsed_profile_sidebar_verified_via_readonly_tab(self):
        status, message, events, visits = self._collapsed_profile_nav_attempt(task="unfollow")
        self.assertEqual(status, "ok", message)
        self.assertEqual(events, ["open", "unfollow", "confirmed"])
        self.assertTrue(any("/my.profile/" in u for u in visits))

    def test_collapsed_sidebar_wrong_logged_in_owner_never_clicks(self):
        status, message, events, visits = self._collapsed_profile_nav_attempt(proven_owner="different.account")
        self.assertEqual(status, "blocked", message)
        self.assertEqual(events, [])
        self.assertTrue(any("/my.profile/" in u for u in visits))

    def test_conflicting_semantic_nav_identity_never_falls_back_to_suggested_owner(self):
        status, message, events, visits = self._collapsed_profile_nav_attempt(misleading_nav=True)
        self.assertEqual(status, "blocked", message)
        self.assertEqual(events, [])
        self.assertFalse(any("/my.profile/" in u for u in visits),
                         "Strong conflicting nav identity must immediately stop actions")

    def test_cancel_pending_succeeds_with_collapsed_profile_nav_and_verified_owner_tab(self):
        # Real user case: Home identifies the owner, but nav disappears on
        # target profiles. A read-only own-profile tab must prove identity.
        target = fake_profile(request_unfollow=True).replace(
            '<nav><a href="/my.profile/" aria-label="Profile">Profile</a></nav>', ''
        ).replace('>Following</button>', '>Requested</button>')
        owner = ('<html><body><header><h2>my.profile</h2>'
                 '<button>Edit profile</button></header></body></html>')
        self.page.route("https://www.instagram.com/**",
            lambda route: route.fulfill(
                status=200, content_type="text/html",
                body=owner if route.request.url.rstrip("/").endswith("/my.profile")
                     else target))
        status,message=perform_visible_action(
            self.page,"target.user","cancel","my.profile",lambda _:True)
        self.assertEqual(status,"ok",message)
        self.assertEqual(self.page.evaluate("window.__steps"),["open","confirmed"])
        self.page.unroute_all()

    def test_cancel_pending_wrong_owner_cannot_click_with_hidden_nav(self):
        target = fake_profile(request_unfollow=True).replace(
            '<nav><a href="/my.profile/" aria-label="Profile">Profile</a></nav>', ''
        ).replace('>Following</button>', '>Requested</button>')
        impostor = ('<html><body><header><h2>impostor.account</h2>'
                    '<button>Edit profile</button></header></body></html>')
        self.page.route("https://www.instagram.com/**",
            lambda route: route.fulfill(
                status=200, content_type="text/html",
                body=impostor if route.request.url.rstrip("/").endswith("/my.profile")
                     else target))
        status,message=perform_visible_action(
            self.page,"target.user","cancel","my.profile",lambda _:True)
        self.assertEqual(status,"blocked",message)
        self.assertEqual(self.page.evaluate("window.__steps"),[])
        self.page.unroute_all()

    def test_public_english_popup(self):
        status, message, events = self.attempt()
        self.assertEqual(status, "ok", message)
        self.assertEqual(events, ["open", "unfollow", "confirmed"])

    def test_public_spanish_popup(self):
        status, message, events = self.attempt(locale="es")
        self.assertEqual(status, "ok", message)
        self.assertEqual(events, ["open", "unfollow", "confirmed"])

    def test_mutual_public_unfollow_ends_follow_back(self):
        status, message, events = self.attempt(result="followback")
        self.assertEqual(status, "ok", message)
        self.assertIn("Follow Back", message)
        self.assertIn("still follows you", message)
        self.assertEqual(events, ["open", "unfollow", "confirmed"])

    def test_mutual_public_unfollow_spanish_ends_seguir_tambien(self):
        status, message, events = self.attempt(locale="es", result="followback")
        self.assertEqual(status, "ok", message)
        self.assertIn("Follow Back", message)
        self.assertEqual(events, ["open", "unfollow", "confirmed"])

    def test_private_english_extra_confirmation(self):
        status, message, events = self.attempt(private=True)
        self.assertEqual(status, "ok", message)
        self.assertEqual(events, ["open", "unfollow", "confirmed"])

    def test_private_spanish_extra_confirmation(self):
        status, message, events = self.attempt(locale="es", private=True)
        self.assertEqual(status, "ok", message)
        self.assertEqual(events, ["open", "unfollow", "confirmed"])

    def test_protected_no_click(self):
        status, message, events = self.attempt(protected=True)
        self.assertEqual(status, "skipped", message)
        self.assertEqual(events, [])

    def test_wrong_account_no_click(self):
        status, message, events = self.attempt(account="not.my.profile")
        self.assertEqual(status, "blocked", message)
        self.assertEqual(events, [])

    def test_unverified_final_state_not_success(self):
        status, message, events = self.attempt(result="unchanged")
        self.assertEqual(status, "review", message)
        self.assertEqual(events, ["open", "unfollow", "confirmed"])

    def test_pending_list_outdated_but_now_following_no_click(self):
        status,message,events=self.attempt(task="cancel",pending_already_following=True)
        self.assertEqual(status,"review",message)
        self.assertIn("Outdated pending request",message)
        self.assertEqual(events,[])

    def test_pending_list_outdated_but_now_siguiendo_no_click(self):
        status,message,events=self.attempt(task="cancel",locale="es",
                                           pending_already_following=True)
        self.assertEqual(status,"review",message)
        self.assertIn("Outdated pending request",message)
        self.assertEqual(events,[])

    def test_missing_profile_relationship_no_click(self):
        status,message,events=self.attempt(task="cancel",missing_profile=True)
        self.assertEqual(status,"review",message)
        self.assertIn("does not show the state required",message)
        self.assertEqual(events,[])

    def test_pending_request_dialog_unfollow_english(self):
        status, message, events = self.attempt(task="cancel", request_unfollow=True)
        self.assertEqual(status, "ok", message)
        self.assertEqual(events, ["open", "confirmed"])

    def test_pending_request_dialog_unfollow_spanish(self):
        status, message, events = self.attempt(task="cancel", locale="es",
                                               request_unfollow=True)
        self.assertEqual(status, "ok", message)
        self.assertEqual(events, ["open", "confirmed"])

    def test_pending_unfollow_no_warning_must_not_click(self):
        status, message, events = self.attempt(task="cancel", request_unfollow=True,
                                               include_warning=False)
        self.assertEqual(status, "review", message)
        self.assertEqual(events, ["open"])

    def test_pending_unfollow_does_not_match_username_extension(self):
        status, message, events = self.attempt(task="cancel", request_unfollow=True,
                                               warning_handle="target.user.another")
        self.assertEqual(status, "review", message)
        self.assertEqual(events, ["open"])

    def test_pending_unfollow_wrong_handle_must_not_click(self):
        status, message, events = self.attempt(task="cancel", request_unfollow=True,
                                               warning_handle="not.target.user")
        self.assertEqual(status, "review", message)
        self.assertEqual(events, ["open"])

    def test_pending_unfollow_protected_no_click(self):
        status, message, events = self.attempt(task="cancel", request_unfollow=True,
                                               protected=True)
        self.assertEqual(status, "skipped", message)
        self.assertEqual(events, [])

    def test_pending_unfollow_no_verified_follow_is_review(self):
        status, message, events = self.attempt(task="cancel", request_unfollow=True,
                                               result="unchanged")
        self.assertEqual(status, "review", message)
        self.assertEqual(events, ["open", "confirmed"])

    def test_pending_request_follow_state_is_not_follow_back(self):
        status, message, events = self.attempt(task="cancel", request_unfollow=True)
        self.assertEqual(status, "ok", message)
        self.assertIn("Action confirmed: Follow.", message)
        self.assertNotIn("person still follows you", message)
        self.assertEqual(events, ["open", "confirmed"])

    def test_request_cancel_english(self):
        status, message, events = self.attempt(task="cancel")
        self.assertEqual(status, "ok", message)
        self.assertEqual(events, ["open", "confirmed"])

    def test_request_cancel_spanish(self):
        status, message, events = self.attempt(task="cancel",locale="es")
        self.assertEqual(status, "ok", message)
        self.assertEqual(events, ["open", "confirmed"])


if __name__ == "__main__":
    unittest.main()
