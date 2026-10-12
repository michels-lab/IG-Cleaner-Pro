"""Real Chromium DOM tests against offline Instagram-like pages.

All www.instagram.com navigation is intercepted locally: never log into or
change a real account. These tests exercise actual Playwright selectors/clicks.
"""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from profile_actions import perform_visible_action, classify_followback_search, perform_visible_followback_audit

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
        self.assertIn("aún te sigue", message)
        self.assertEqual(events, ["open", "unfollow", "confirmed"])

    def test_mutual_public_unfollow_spanish_ends_seguir_tambien(self):
        status, message, events = self.attempt(locale="es", result="followback")
        self.assertEqual(status, "ok", message)
        self.assertIn("Seguir también", message)
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
        self.assertIn("Pendiente desactualizado",message)
        self.assertEqual(events,[])

    def test_pending_list_outdated_but_now_siguiendo_no_click(self):
        status,message,events=self.attempt(task="cancel",locale="es",
                                           pending_already_following=True)
        self.assertEqual(status,"review",message)
        self.assertIn("Pendiente desactualizado",message)
        self.assertEqual(events,[])

    def test_missing_profile_relationship_no_click(self):
        status,message,events=self.attempt(task="cancel",missing_profile=True)
        self.assertEqual(status,"review",message)
        self.assertIn("no muestra el estado necesario",message)
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
        self.assertIn("Follow / Seguir", message)
        self.assertNotIn("La persona aún te sigue", message)
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
