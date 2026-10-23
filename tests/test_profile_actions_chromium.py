"""Real Chromium DOM tests against offline Instagram-like pages.

All www.instagram.com navigation is intercepted locally: never log into or
change a real account. These tests exercise actual Playwright selectors/clicks.
"""
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from profile_actions import perform_visible_action, classify_followback_search, perform_visible_followback_audit
from profile_counts_instagram import signed_in_handle, read_following_visible, FollowingControlUnavailable

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None


def fake_profile(locale="en", private=False, account="my.profile", result="follow",
                 blocked=False, request_unfollow=False, warning_handle="target.user",
                 include_warning=True, persist=True):
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
           requestUnfollow={str(request_unfollow).lower()},
           persistenceEnabled={str(persist).lower()};
     // Browser-local fixture ONLY: simulate Instagram committing a relationship
     // to an independent state retained over a fresh document navigation.
     // Real negative server-rejection fixtures disable this persistence.
     // Hash the original fixture markup so separate subtests and layouts
     // in the SAME Playwright tab never inherit each other's fake results.
     const fixtureMarkup=document.body.innerHTML;
     let fixtureHash=2166136261;
     for(let i=0;i<fixtureMarkup.length;i++)
       fixtureHash=Math.imul(fixtureHash ^ fixtureMarkup.charCodeAt(i),16777619);
     const suffix=(fixtureHash>>>0).toString(36);
     const fakeRelationKey='igc_test_server_relationship_v1_'+suffix;
     const fakeStepsKey='igc_test_step_history_v1_'+suffix;
     const fakeGet=k=>{{ try {{ return sessionStorage.getItem(k) }} catch(_) {{ return null }} }};
     const fakeSet=(k,v)=>{{ try {{ sessionStorage.setItem(k,v) }} catch(_) {{ }} }};
     window.__steps=JSON.parse(fakeGet(fakeStepsKey)||'[]');
     const lastCommitted=fakeGet(fakeRelationKey);
     if(lastCommitted&&persistenceEnabled) {{
       document.addEventListener('DOMContentLoaded',()=>{{
         const control=document.querySelector('#relationship');
         if(control)control.textContent=lastCommitted==='followback'
           ?(document.documentElement.lang==='es'?'Seguir también':'Follow Back')
           :(document.documentElement.lang==='es'?'Seguir':'Follow');
       }});
     }}
     function recordStep(value) {{
       window.__steps.push(value);
       fakeSet(fakeStepsKey,JSON.stringify(window.__steps));
       console.log("IGC_STEP:" + value);
     }}
     function openRelationship() {{
       recordStep('open');
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
       recordStep('unfollow');
       document.querySelector('#action-menu').style.display='none';
       if(privateFlow)document.querySelector('#private-confirm').style.display='block';
       else finishChange();
     }}
     function dismissRequest() {{
       recordStep('dismiss');
       document.querySelector('#request-confirm').style.display='none';
     }}
     function finishChange() {{
       recordStep('confirmed');
       document.querySelector('#action-menu').style.display='none';
       document.querySelector('#private-confirm').style.display='none';
       document.querySelector('#request-confirm').style.display='none';
       if(result==='follow')document.querySelector('#relationship').textContent=label;
       if(result==='followback')document.querySelector('#relationship').textContent=
         document.documentElement.lang==='es'?'Seguir también':'Follow Back';
       if(persistenceEnabled&&!blocked&&(result==='follow'||result==='followback'))
         fakeSet(fakeRelationKey,result);
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
        # Keep offline negative fixtures fast; production still waits 20s.
        # Positive delayed hydration fixtures take 1.7s and remain meaningful.
        self._wait_override = patch("profile_actions.ACTION_CONTROL_WAIT_MS", 3000)
        self._wait_override.start()
        self.context = self.browser.new_context()
        self.page = self.context.new_page()

    def tearDown(self):
        try:
            self.context.close()
        finally:
            self._wait_override.stop()

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
        # Console events survive the final read-only refresh while page globals do not.
        recorded_steps = []
        self.page.on("console", lambda msg: recorded_steps.append(msg.text.split("IGC_STEP:", 1)[1])
                     if msg.text.startswith("IGC_STEP:") else None)
        # An optimistic browser label is not a saved Instagram relationship.
        # Offline responses emulate a real server that persists the new state
        # only AFTER the mutation was successfully clicked. The fresh GET
        # produces independent evidence and must never trigger another click.
        initial = html
        starting_label = ">Siguiendo</button>" if locale == "es" else ">Following</button>"
        if task == "cancel" and not pending_already_following and not missing_profile:
            initial = initial.replace(
                starting_label,
                ">Solicitado</button>" if locale == "es" else ">Requested</button>", 1)
        if missing_profile:
            initial = initial.replace(starting_label, ">Unknown status</button>", 1)
        persisted = initial
        if result in ("follow", "followback") and not blocked:
            persisted = html.replace(
                ">Siguiendo</button>" if locale == "es" else ">Following</button>",
                (">Seguir también</button>" if result == "followback" else ">Seguir</button>")
                if locale == "es" else
                (">Follow Back</button>" if result == "followback" else ">Follow</button>"),
                1)
        if result == "unchanged" or blocked:
            persisted = initial
        visits = []
        def offline_route(route):
            visits.append(route.request.url)
            route.fulfill(status=200, content_type="text/html",
                          body=initial if len(visits) == 1 else persisted)
        self.page.route("https://www.instagram.com/**", offline_route)
        self._last_action_visits = visits
        status, message = perform_visible_action(
            self.page, "target.user", task, "my.profile",
            (lambda _: not protected))
        return status, message, recorded_steps


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
             '<nav><button aria-label="Profile">☻</button></nav>'))
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
        self.context.route("https://www.instagram.com/**", route)
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
        self.context.route("https://www.instagram.com/**",
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
        self.context.route("https://www.instagram.com/**",
            lambda route: route.fulfill(
                status=200, content_type="text/html",
                body=impostor if route.request.url.rstrip("/").endswith("/my.profile")
                     else target))
        status,message=perform_visible_action(
            self.page,"target.user","cancel","my.profile",lambda _:True)
        self.assertEqual(status,"blocked",message)
        self.assertEqual(self.page.evaluate("window.__steps"),[])
        self.page.unroute_all()

    def _main_role_button_unfollow(self, locale="en", target_heading="target.user",
                                   role_button=True, duplicate=False):
        """Real Chromium, offline: Instagram profile hero without <header>."""
        label = "Siguiendo" if locale == "es" else "Following"
        original = fake_profile(locale=locale)
        legacy = ('    <header>\n      <h1>target.user</h1>\n'
                  f'      <button id="relationship" onclick="openRelationship()">{label}</button>\n'
                  '    </header>')
        control = (f'<div id="relationship" role="button" tabindex="0" '
                   f'onclick="openRelationship()">{label} ▾</div>'
                   if role_button else
                   f'<a href="/my.profile/following/">{label}</a>')
        other = (f'<div role="button" onclick="window.__otherClicked=true">'
                 f'{label}</div>' if duplicate else '')
        hero = (f'<main><section><h2>{target_heading}</h2>'
                f'{control}{other}</section></main>')
        self.assertIn(legacy, original)
        html = original.replace(legacy, hero)
        self.context.route("https://www.instagram.com/**",
            lambda route: route.fulfill(status=200, content_type="text/html", body=html))
        events = []
        self.page.on("console", lambda msg: events.append(msg.text.split("IGC_STEP:", 1)[1])
                     if msg.text.startswith("IGC_STEP:") else None)
        return events

    def test_unfollow_from_main_role_button_with_dropdown_caret(self):
        for locale in ("en", "es"):
            with self.subTest(locale=locale):
                self.context.unroute_all()
                events = self._main_role_button_unfollow(locale=locale)
                status, message = perform_visible_action(
                    self.page, "target.user", "unfollow", "my.profile", lambda _: True)
                self.assertEqual(status, "ok", message)
                self.assertEqual(events, ["open", "unfollow", "confirmed"])
                self.assertIn("no longer follow", message)

    def test_following_count_link_never_becomes_an_unfollow_click(self):
        events = self._main_role_button_unfollow(role_button=False)
        status, message = perform_visible_action(
            self.page, "target.user", "unfollow", "my.profile", lambda _: True)
        self.assertEqual(status, "review")
        self.assertIn("nothing clicked", message)
        self.assertEqual(events, [])

    def test_unrelated_main_following_button_cannot_replace_target_heading(self):
        events = self._main_role_button_unfollow(target_heading="someone.else")
        status, message = perform_visible_action(
            self.page, "target.user", "unfollow", "my.profile", lambda _: True)
        self.assertEqual(status, "blocked")
        self.assertIn("heading", message)
        self.assertEqual(events, [])

    def test_ambiguous_main_following_buttons_never_click(self):
        events = self._main_role_button_unfollow(duplicate=True)
        with self.assertRaisesRegex(RuntimeError, "Multiple equivalent options"):
            perform_visible_action(
                self.page, "target.user", "unfollow", "my.profile", lambda _: True)
        self.assertEqual(events, [])

    def _visual_profile_hero(self, *, language="en", control_kind="tabindex",
                             profile="target.user", duplicate=False,
                             unrelated=False):
        """Instagram's non-semantic real-life span/div profile hero, offline."""
        original = fake_profile(locale=language)
        following = "Siguiendo" if language == "es" else "Following"
        old = ('    <header>\n      <h1>target.user</h1>\n'
               f'      <button id="relationship" onclick="openRelationship()">{following}</button>\n'
               '    </header>')
        self.assertIn(old, original)
        if control_kind == "tabindex":
            action = (f'<div id="relationship" tabindex="0" '
                      f'onclick="openRelationship()"><span>{following}</span>'
                      ' <svg aria-hidden="true"><path/></svg></div>')
        elif control_kind == "role":
            action = (f'<div id="relationship" role="button" '
                      f'onclick="openRelationship()"><span>{following}</span>'
                      ' <span aria-hidden="true">∨</span></div>')
        elif control_kind == "button":
            action = (f'<button id="relationship" '
                      f'onclick="openRelationship()">{following}</button>')
        else:
            action = f'<a href="/target.user/following/">{following}</a>'
        additional = (f'<div role="button" onclick="window.__ambiguous=true">'
                      f'{following}</div>' if duplicate else "")
        suggestion = (f'<aside><span>suggested.person</span>'
                      f'<div role="button" onclick="window.__unrelated=true">'
                      f'{following}</div></aside>' if unrelated else "")
        # No semantic heading anywhere in the main profile.
        new = (f'<main><section><div><span>{profile}</span></div>'
               f'<div style="margin-top:36px">{action}{additional}</div>'
               f'</section>{suggestion}</main>')
        html = original.replace(old, new)
        self.context.route("https://www.instagram.com/**",
            lambda route: route.fulfill(status=200, content_type="text/html", body=html))
        events = []
        self.page.on("console", lambda msg: events.append(msg.text.split("IGC_STEP:", 1)[1])
                     if msg.text.startswith("IGC_STEP:") else None)
        return events

    def test_following_visible_span_username_and_real_clickable_div(self):
        for language, kind in (("en", "tabindex"), ("es", "role"), ("en", "button")):
            with self.subTest(language=language, kind=kind):
                self.context.unroute_all()
                events = self._visual_profile_hero(language=language, control_kind=kind)
                result, message = perform_visible_action(
                    self.page, "target.user", "unfollow", "my.profile", lambda _: True)
                self.assertEqual(result, "ok", message)
                self.assertEqual(events, ["open", "unfollow", "confirmed"])

    def test_nonsemantic_pointer_following_div_is_verified_and_clicked(self):
        original = fake_profile()
        old = ('    <header>\n      <h1>target.user</h1>\n'
               '      <button id="relationship" onclick="openRelationship()">Following</button>\n'
               '    </header>')
        hero = ('<main><section><span>target.user</span>'
                '<div style="margin-top:30px;cursor:pointer" id="relationship" '
                'onclick="openRelationship()"><span>Following</span>'
                '<svg aria-hidden="true"></svg></div></section></main>')
        self.assertIn(old, original)
        html = original.replace(old, hero)
        self.context.route("https://www.instagram.com/**",
            lambda route: route.fulfill(status=200, content_type="text/html", body=html))
        status, message = perform_visible_action(
            self.page, "target.user", "unfollow", "my.profile", lambda _: True)
        self.assertEqual(status, "ok", message)
        self.assertEqual(self.page.evaluate("window.__steps"),
                         ["open", "unfollow", "confirmed"])

    def test_pointer_text_inside_following_counter_link_must_not_click(self):
        original = fake_profile()
        old = ('    <header>\n      <h1>target.user</h1>\n'
               '      <button id="relationship" onclick="openRelationship()">Following</button>\n'
               '    </header>')
        html = original.replace(old, (
            '<main><span>target.user</span>'
            '<a href="/target.user/following/" style="cursor:pointer">'
            '<span>Following</span></a></main>'))
        self.context.route("https://www.instagram.com/**",
            lambda route: route.fulfill(status=200, content_type="text/html", body=html))
        status, message = perform_visible_action(
            self.page, "target.user", "unfollow", "my.profile", lambda _: True)
        self.assertEqual(status, "review", message)
        self.assertEqual(self.page.evaluate("window.__steps"), [])

    def test_ambiguous_two_pointer_following_controls_do_not_click(self):
        original = fake_profile()
        old = ('    <header>\n      <h1>target.user</h1>\n'
               '      <button id="relationship" onclick="openRelationship()">Following</button>\n'
               '    </header>')
        html = original.replace(old, (
            '<main><span>target.user</span><section style="margin-top:30px">'
            '<div style="cursor:pointer" id="relationship" onclick="openRelationship()">'
            '<span>Following</span></div>'
            '<div style="cursor:pointer" onclick="window.__unexpected=true">'
            '<span>Following</span></div></section></main>'))
        self.context.route("https://www.instagram.com/**",
            lambda route: route.fulfill(status=200, content_type="text/html", body=html))
        with self.assertRaisesRegex(RuntimeError, "ambiguous visual"):
            perform_visible_action(
                self.page, "target.user", "unfollow", "my.profile", lambda _: True)
        self.assertEqual(self.page.evaluate("window.__steps"), [])
        self.assertFalse(self.page.evaluate("Boolean(window.__unexpected)"))

    def test_unfollow_refresh_can_confirm_delayed_follow_state_without_reclick(self):
        route_count = {"visits": 0}
        events = []
        def route(request):
            route_count["visits"] += 1
            html = fake_profile(result="unchanged")
            if route_count["visits"] >= 2:
                html = html.replace('>Following</button>', '>Follow</button>')
            request.fulfill(status=200, content_type="text/html", body=html)
        self.context.route("https://www.instagram.com/**", route)
        self.page.on("console", lambda msg: events.append(msg.text.split("IGC_STEP:",1)[1])
                     if msg.text.startswith("IGC_STEP:") else None)
        result, message = perform_visible_action(
            self.page, "target.user", "unfollow", "my.profile", lambda _: True)
        self.assertEqual(result, "ok", message)
        self.assertIn("read-only profile refresh", message)
        self.assertEqual(events, ["open", "unfollow", "confirmed"])
        self.assertEqual(route_count["visits"], 2)

    def test_non_clickable_following_text_records_read_only_layout_diagnostic(self):
        events = self._visual_profile_hero(control_kind="link")
        result, message = perform_visible_action(
            self.page, "target.user", "unfollow", "my.profile", lambda _: True)
        self.assertEqual(result, "review")
        self.assertIn("nothing clicked", message)
        self.assertIn("Profile layout: main=yes, exact username=yes", message)
        self.assertIn("named interactive controls=0", message)
        self.assertEqual(events, [])

    def test_following_in_suggested_aside_is_not_a_target_button(self):
        events = self._visual_profile_hero(control_kind="link", unrelated=True)
        result, message = perform_visible_action(
            self.page, "target.user", "unfollow", "my.profile", lambda _: True)
        self.assertEqual(result, "review")
        self.assertEqual(events, [])
        self.assertFalse(self.page.evaluate("Boolean(window.__unrelated)"))

    def test_visual_hero_wrong_username_cannot_click_following(self):
        events = self._visual_profile_hero(profile="not.target.user")
        result, message = perform_visible_action(
            self.page, "target.user", "unfollow", "my.profile", lambda _: True)
        self.assertEqual(result, "blocked")
        self.assertIn("exact username", message)
        self.assertEqual(events, [])

    def test_visual_hero_two_following_actions_never_click(self):
        events = self._visual_profile_hero(duplicate=True)
        with self.assertRaisesRegex(RuntimeError, "Multiple matching profile action controls"):
            perform_visible_action(
                self.page, "target.user", "unfollow", "my.profile", lambda _: True)
        self.assertEqual(events, [])

    def test_profile_shell_waits_for_delayed_instagram_render(self):
        html = fake_profile()
        ready = html.replace("<header>", '<header style="display:none">', 1)
        ready = ready.replace("</script>", (
            "setTimeout(() => document.querySelector('header').style.display='', 1700);"
            "</script>"))
        self.context.route("https://www.instagram.com/**",
            lambda route: route.fulfill(status=200, content_type="text/html", body=ready))
        waits = []
        result, message = perform_visible_action(
            self.page, "target.user", "unfollow", "my.profile",
            lambda _: True, on_wait=lambda phase, elapsed, maximum:
                waits.append((phase, elapsed, maximum)))
        self.assertEqual(result, "ok", message)
        self.assertTrue(any(item[0] == "loading_profile" for item in waits))
        self.assertEqual(self.page.evaluate("window.__steps"),
                         ["open", "unfollow", "confirmed"])

    def test_missing_profile_shell_waits_and_reports_without_click(self):
        from unittest.mock import patch
        import profile_actions
        html = '<html><body><main style="display:none"></main></body></html>'
        self.context.route("https://www.instagram.com/**",
            lambda route: route.fulfill(status=200, content_type="text/html", body=html))
        waits = []
        with patch.object(profile_actions, "ACTION_CONTROL_WAIT_MS", 1100):
            result, message = perform_visible_action(
                self.page, "target.user", "unfollow", "my.profile",
                lambda _: True, on_wait=lambda phase, elapsed, maximum:
                    waits.append((phase, elapsed, maximum)))
        self.assertEqual(result, "review", message)
        self.assertIn("Waiting timed out: profile identity", message)
        self.assertIn("No action clicked.", message)
        self.assertTrue(any(p == "loading_profile" for p, _, _ in waits))
        self.assertEqual(profile_actions._action_issue("unfollow", result, message),
                         "profile_load_timeout")
        self.assertTrue(profile_actions._preclick_no_action({
            "status": result, "issue": "profile_load_timeout", "message": message}))

    def test_missing_following_control_is_visible_wait_then_review_not_skip(self):
        from unittest.mock import patch
        import profile_actions
        html = fake_profile().replace(
            'id="relationship" onclick="openRelationship()"',
            'id="relationship" style="display:none" onclick="openRelationship()"')
        self.context.route("https://www.instagram.com/**",
            lambda route: route.fulfill(status=200, content_type="text/html", body=html))
        waits = []
        with patch.object(profile_actions, "ACTION_CONTROL_WAIT_MS", 1100):
            result, message = perform_visible_action(
                self.page, "target.user", "unfollow", "my.profile",
                lambda _: True, on_wait=lambda phase, elapsed, maximum:
                    waits.append((phase, elapsed, maximum)))
        self.assertEqual(result, "review", message)
        self.assertIn("Following/Siguiendo", message)
        self.assertIn("No action clicked.", message)
        self.assertTrue(any(p == "waiting_relationship_control" for p, _, _ in waits))
        self.assertEqual(self.page.evaluate("window.__steps"), [])
        self.assertEqual(profile_actions._action_issue("unfollow", result, message),
                         "profile_load_timeout")

    def test_prefetched_profile_does_not_navigate_twice_before_action(self):
        html = fake_profile()
        visits = []
        def route(request):
            visits.append(request.request.url)
            request.fulfill(status=200, content_type="text/html", body=html)
        self.context.route("https://www.instagram.com/**", route)
        self.page.goto("https://www.instagram.com/target.user/", wait_until="commit")
        result, message = perform_visible_action(
            self.page, "target.user", "unfollow", "my.profile",
            lambda _: True, preloaded=True)
        self.assertEqual(result, "ok", message)
        self.assertEqual(
            sum("/target.user/" in url for url in visits), 2,
            "Preloaded target uses one initial GET and exactly one post-click "
            "independent verification GET; there must be no pre-click double navigation")
        self.assertEqual(self.page.evaluate("window.__steps"),
                         ["open", "unfollow", "confirmed"])

    def test_same_url_without_prefetch_must_reload_after_fixture_changes(self):
        self.context.route("https://www.instagram.com/**",
            lambda route: route.fulfill(status=200, content_type="text/html",
                                        body=fake_profile()))
        self.page.goto("https://www.instagram.com/target.user/")
        self.assertEqual(self.page.locator("#relationship").inner_text(), "Following")
        self.context.unroute_all()
        spanish = fake_profile(locale="es")
        self.context.route("https://www.instagram.com/**",
            lambda route: route.fulfill(status=200, content_type="text/html",
                                        body=spanish))
        result, message = perform_visible_action(
            self.page, "target.user", "unfollow", "my.profile", lambda _: True)
        self.assertEqual(result, "ok", message)
        self.assertEqual(self.page.evaluate("window.__steps"),
                         ["open", "unfollow", "confirmed"])

    def test_delayed_profile_control_waits_for_visible_following(self):
        # A real page may hydrate its Following button after DOMContentLoaded.
        html = fake_profile().replace(
            'id="relationship" onclick="openRelationship()"',
            'id="relationship" style="display:none" onclick="openRelationship()"')
        html = html.replace('</script>', (
            "setTimeout(() => { document.querySelector('#relationship').style.display = ''; }, 1700);"
            "</script>"))
        self.context.route("https://www.instagram.com/**",
            lambda route: route.fulfill(status=200, content_type="text/html", body=html))
        result, message = perform_visible_action(
            self.page, "target.user", "unfollow", "my.profile", lambda _: True)
        self.assertEqual(result, "ok", message)
        self.assertEqual(self.page.evaluate("window.__steps"),
                         ["open", "unfollow", "confirmed"])

    def test_delayed_unfollow_menu_waits_without_extra_click(self):
        html = fake_profile().replace(
            "document.querySelector('#action-menu').style.display='block';",
            "setTimeout(() => { document.querySelector('#action-menu').style.display='block'; }, 1700);")
        self.context.route("https://www.instagram.com/**",
            lambda route: route.fulfill(status=200, content_type="text/html", body=html))
        result, message = perform_visible_action(
            self.page, "target.user", "unfollow", "my.profile", lambda _: True)
        self.assertEqual(result, "ok", message)
        self.assertEqual(self.page.evaluate("window.__steps"),
                         ["open", "unfollow", "confirmed"])

    def test_post_click_transient_owner_failure_rechecks_without_reclick(self):
        from unittest.mock import patch
        import profile_actions
        html = fake_profile()
        self.context.route("https://www.instagram.com/**",
            lambda route: route.fulfill(status=200, content_type="text/html", body=html))
        actual = profile_actions._verified_action_owner
        observations = {"temporary_misses": 0}
        def delayed_identity(page, expected):
            # One read-only identity failure immediately after a genuine click.
            if (page.evaluate("window.__steps.includes('confirmed')")
                    and observations["temporary_misses"] == 0):
                observations["temporary_misses"] += 1
                return False
            return actual(page, expected)
        with patch.object(profile_actions, "_verified_action_owner", delayed_identity):
            result, message = perform_visible_action(
                self.page, "target.user", "unfollow", "my.profile", lambda _: True)
        self.assertEqual(observations["temporary_misses"], 1)
        self.assertEqual(result, "ok", message)
        self.assertEqual(self.page.evaluate("window.__steps"),
                         ["open", "unfollow", "confirmed"])

    def test_cancel_no_request_verified_without_click_public_private_locales(self):
        import profile_actions
        for locale, label, private in (
            ("en", "Follow", False),
            ("en", "Follow Back", True),
            ("es", "Seguir", False),
            ("es", "Seguir también", True),
        ):
            with self.subTest(locale=locale, label=label, private=private):
                self.context.unroute_all()
                original = "Siguiendo" if locale == "es" else "Following"
                html = fake_profile(locale=locale, private=private).replace(
                    ">" + original + "</button>", ">" + label + "</button>", 1)
                self.context.route("https://www.instagram.com/**",
                    lambda route: route.fulfill(
                        status=200, content_type="text/html", body=html))
                with patch.object(profile_actions, "ACTION_CONTROL_WAIT_MS", 2000), \
                     patch.object(profile_actions, "CANCEL_NO_REQUEST_MIN_WAIT_MS", 700):
                    status, message = perform_visible_action(
                        self.page, "target.user", "cancel", "my.profile", lambda _: True)
                self.assertEqual(status, "already_not_requested", message)
                self.assertIn("No Cancel Request clicked", message)
                self.assertEqual(self.page.evaluate("window.__steps"), [])

    def test_cancel_delayed_requested_takes_precedence_over_follow(self):
        import profile_actions
        html = fake_profile().replace(">Following</button>", ">Follow</button>", 1)
        html = html.replace("</script>", (
            "setTimeout(() => document.querySelector('#relationship').textContent='Requested', 700);"
            "</script>"))
        visits = []
        persisted = fake_profile().replace(">Following</button>", ">Follow</button>", 1)
        def serve(route):
            visits.append(route.request.url)
            route.fulfill(status=200, content_type="text/html",
                          body=html if len(visits) == 1 else persisted)
        self.context.route("https://www.instagram.com/**", serve)
        with patch.object(profile_actions, "ACTION_CONTROL_WAIT_MS", 2200), \
             patch.object(profile_actions, "CANCEL_NO_REQUEST_MIN_WAIT_MS", 1300):
            status, message = perform_visible_action(
                self.page, "target.user", "cancel", "my.profile", lambda _: True)
        self.assertEqual(status, "ok", message)
        self.assertEqual(self.page.evaluate("window.__steps"), ["open", "confirmed"])

    def test_cancel_sidebar_follow_is_not_exact_target_evidence(self):
        import profile_actions
        html = fake_profile().replace(">Following</button>", ">Loading...</button>", 1)
        html = html.replace("<header>", '<aside><button>Follow</button></aside><header>', 1)
        self.context.route("https://www.instagram.com/**",
            lambda route: route.fulfill(status=200, content_type="text/html", body=html))
        with patch.object(profile_actions, "ACTION_CONTROL_WAIT_MS", 650), \
             patch.object(profile_actions, "CANCEL_NO_REQUEST_MIN_WAIT_MS", 0):
            status, message = perform_visible_action(
                self.page, "target.user", "cancel", "my.profile", lambda _: True)
        self.assertEqual(status, "review", message)
        self.assertEqual(self.page.evaluate("window.__steps"), [])

    def test_already_not_following_advances_without_a_relationship_click(self):
        """Owner request: Follow / Follow Back means no Unfollow is needed."""
        import profile_actions
        for locale, label in (("en", "Follow"), ("es", "Seguir"),
                              ("en", "Follow Back"), ("es", "Seguir también")):
            with self.subTest(locale=locale, label=label):
                self.context.unroute_all()
                old = "Siguiendo" if locale == "es" else "Following"
                html = fake_profile(locale=locale).replace(
                    ">" + old + "</button>", ">" + label + "</button>", 1)
                self.context.route("https://www.instagram.com/**",
                    lambda route: route.fulfill(
                        status=200, content_type="text/html", body=html))
                status, message = perform_visible_action(
                    self.page, "target.user", "unfollow", "my.profile", lambda _: True)
                self.assertEqual(status, "already_not_following", message)
                self.assertIn("No Unfollow", message)
                self.assertEqual(self.page.evaluate("window.__steps"), [])
                self.assertEqual(profile_actions._action_issue("unfollow", status, message), "")

    def test_delayed_visible_follow_is_already_not_following_without_click(self):
        html = fake_profile().replace(">Following</button>", ">Loading...</button>", 1)
        html = html.replace("</script>", (
            "setTimeout(() => document.querySelector('#relationship').textContent='Follow', 650);"
            "</script>"))
        self.context.route("https://www.instagram.com/**",
            lambda route: route.fulfill(status=200, content_type="text/html", body=html))
        status, message = perform_visible_action(
            self.page, "target.user", "unfollow", "my.profile", lambda _: True)
        self.assertEqual(status, "already_not_following", message)
        self.assertEqual(self.page.evaluate("window.__steps"), [])

    def test_other_account_follow_button_does_not_skip_real_following(self):
        html = fake_profile().replace(
            "<header>", '<aside><button>Follow</button></aside><header>', 1)
        self.context.route("https://www.instagram.com/**",
            lambda route: route.fulfill(status=200, content_type="text/html", body=html))
        status, message = perform_visible_action(
            self.page, "target.user", "unfollow", "my.profile", lambda _: True)
        self.assertEqual(status, "ok", message)
        self.assertEqual(self.page.evaluate("window.__steps"),
                         ["open", "unfollow", "confirmed"])

    def test_follow_back_with_follows_you_banner_already_not_following(self):
        html = fake_profile().replace(">Following</button>", ">Follow Back</button>", 1)
        html = html.replace("<h1>target.user</h1>",
                            "<h1>target.user</h1><span>Follows you</span>", 1)
        self.context.route("https://www.instagram.com/**",
            lambda route: route.fulfill(status=200, content_type="text/html", body=html))
        status, message = perform_visible_action(
            self.page, "target.user", "unfollow", "my.profile", lambda _: True)
        self.assertEqual(status, "already_not_following", message)
        self.assertEqual(self.page.evaluate("window.__steps"), [])

    def test_public_english_popup(self):
        status, message, events = self.attempt()
        self.assertEqual(status, "ok", message)
        self.assertEqual(events, ["open", "unfollow", "confirmed"])
        self.assertEqual(len(self._last_action_visits), 2,
                         "A successful Unfollow needs its own read-only reload")

    def test_immediate_optimistic_unfollow_follow_is_not_persisted_success(self):
        # The UI flips to Follow after clicking but a freshly loaded server
        # response still says Following. NEVER claim an Unfollow or re-click.
        initial = fake_profile(result="follow", persist=False)
        visits, events = [], []
        self.page.on("console", lambda msg: events.append(msg.text)
                     if msg.text.startswith("IGC_STEP:") else None)
        def serve(route):
            visits.append(route.request.url)
            route.fulfill(status=200, content_type="text/html", body=initial)
        self.page.route("https://www.instagram.com/**", serve)
        status, message = perform_visible_action(
            self.page, "target.user", "unfollow", "my.profile", lambda _: True)
        self.assertEqual(status, "review", message)
        self.assertIn("Do not repeat", message)
        self.assertEqual(len(visits), 2, "One original load and one verification GET")
        self.assertEqual(events, ["IGC_STEP:open", "IGC_STEP:unfollow",
                                  "IGC_STEP:confirmed"])

    def test_immediate_optimistic_cancel_follow_is_not_persisted_success(self):
        # The UI flips to Follow after click; server still replies Requested.
        initial = fake_profile(
            request_unfollow=True, result="follow", persist=False).replace(
            ">Following</button>", ">Requested</button>", 1)
        visits, events = [], []
        self.page.on("console", lambda msg: events.append(msg.text)
                     if msg.text.startswith("IGC_STEP:") else None)
        def serve(route):
            visits.append(route.request.url)
            route.fulfill(status=200, content_type="text/html", body=initial)
        self.page.route("https://www.instagram.com/**", serve)
        status, message = perform_visible_action(
            self.page, "target.user", "cancel", "my.profile", lambda _: True)
        self.assertEqual(status, "review", message)
        self.assertIn("still displays Requested", message)
        self.assertEqual(len(visits), 2)
        self.assertEqual(events, ["IGC_STEP:open", "IGC_STEP:confirmed"])

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

    def test_pending_request_readonly_reload_confirms_delayed_cancel_without_second_click(self):
        first = fake_profile(request_unfollow=True, result="unchanged")
        first = first.replace(">Following</button>", ">Requested</button>")
        second = fake_profile(result="unchanged")
        second = second.replace(">Following</button>", ">Follow</button>")
        log, visits = [], []
        def route(request):
            visits.append(request.request.url)
            request.fulfill(status=200, content_type="text/html",
                            body=first if len(visits) == 1 else second)
        self.page.route("https://www.instagram.com/**", route)
        self.page.on("console", lambda msg: log.append(msg.text)
                     if msg.text.startswith("IGC_STEP:") else None)
        status, message = perform_visible_action(
            self.page, "target.user", "cancel", "my.profile", lambda _: True)
        self.assertEqual(status, "ok", message)
        self.assertIn("read-only profile refresh", message)
        self.assertEqual(log, ["IGC_STEP:open", "IGC_STEP:confirmed"],
                         "No second relationship-changing click after ambiguous result")
        self.assertEqual(len(visits), 2, "Only one safe verification refresh")

    def test_pending_request_refresh_still_requested_needs_manual_review(self):
        first = fake_profile(request_unfollow=True, result="unchanged")
        first = first.replace(">Following</button>", ">Requested</button>")
        events, visits = [], []
        self.page.on("console", lambda msg: events.append(msg.text)
                     if msg.text.startswith("IGC_STEP:") else None)
        def route(request):
            visits.append(request.request.url)
            request.fulfill(status=200, content_type="text/html", body=first)
        self.page.route("https://www.instagram.com/**", route)
        status, message = perform_visible_action(
            self.page, "target.user", "cancel", "my.profile", lambda _: True)
        self.assertEqual(status, "review")
        self.assertIn("still displays Requested", message)
        self.assertIn("Do not repeat", message)
        self.assertEqual(events, ["IGC_STEP:open", "IGC_STEP:confirmed"])
        self.assertEqual(len(visits), 2)
        from profile_actions import _action_issue
        self.assertEqual(_action_issue("cancel", status, message),
                         "pending_cancel_unverified")

    def test_pending_request_readonly_refresh_not_confused_by_following(self):
        first = fake_profile(request_unfollow=True, result="unchanged")
        first = first.replace(">Following</button>", ">Requested</button>")
        second = fake_profile(result="unchanged")
        checks = []
        def route(request):
            checks.append(request.request.url)
            request.fulfill(status=200, content_type="text/html",
                            body=first if len(checks) == 1 else second)
        self.page.route("https://www.instagram.com/**", route)
        status, message = perform_visible_action(
            self.page, "target.user", "cancel", "my.profile", lambda _: True)
        self.assertEqual(status, "review")
        self.assertIn("now displays Following", message)
        self.assertEqual(len(checks), 2)

    def test_pending_request_readonly_refresh_redirect_cannot_prove_cancellation(self):
        first = fake_profile(request_unfollow=True, result="unchanged")
        first = first.replace(">Following</button>", ">Requested</button>")
        page_redirect = "<html><body><h1>Please log in</h1></body></html>"
        checks = []
        def route(request):
            checks.append(request.request.url)
            if len(checks) == 2:
                request.fulfill(status=302, headers={"Location":
                        "https://www.instagram.com/accounts/login/"}, body="")
            else:
                request.fulfill(status=200, content_type="text/html",
                                body=first if len(checks) == 1 else page_redirect)
        self.page.route("https://www.instagram.com/**", route)
        status, message = perform_visible_action(
            self.page, "target.user", "cancel", "my.profile", lambda _: True)
        self.assertNotEqual(status, "ok", "A login redirect must never confirm cancellation")
        self.assertTrue("redirected" in message or "verification" in message,
                        "The anomaly must be clearly reported")

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
