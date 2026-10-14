"""Offline browser acceptance for Instagram Home's visible account switcher.

The user's signed-in account appears next to "Switch" on the desktop Home
rail even when the Profile sidebar link is collapsed/missing. No live login,
network traffic, profile visits or Instagram actions in these tests.
"""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from profile_counts_instagram import (signed_in_handle, own_profile_from_switcher_rows,
                                      verify_selected_owner_profile)

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None


class HomeIdentityEvidenceTests(unittest.TestCase):
    def test_switcher_identity_requires_single_small_row(self):
        self.assertEqual(own_profile_from_switcher_rows([
            {"hrefs": ["/realmichelduarte/", "/realmichelduarte/"]}
        ]), "realmichelduarte")
        self.assertIsNone(own_profile_from_switcher_rows([
            {"hrefs": ["/realmichelduarte/", "/suggested.user/"]}
        ]))
        self.assertIsNone(own_profile_from_switcher_rows([
            {"hrefs": ["/realmichelduarte/"]},
            {"hrefs": ["/another.account/"]}
        ]))
        self.assertIsNone(own_profile_from_switcher_rows([
            {"hrefs": ["/explore/", "/p/abc/"]}
        ]))


@unittest.skipIf(sync_playwright is None, "Install playwright Chromium for DOM fixture tests")
class HomeIdentityChromiumTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch(headless=True)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.pw.stop()

    def setUp(self):
        self.context = self.browser.new_context(viewport={"width": 1180, "height": 860})
        self.page = self.context.new_page()
        self.page.route("**/*", lambda route: route.abort("blockedbyclient"))

    def tearDown(self):
        self.context.close()

    def home(self, switch="Switch", owner="realmichelduarte", multiple=False,
             include_switch=True, hidden=False, login=False, nav=None):
        account = f"""<section id="owner" style="display:flex;width:350px;height:70px;align-items:center;gap:20px">
         <a href="/{owner}/" title="My account"><img alt="Owner" width="36" height="36"> {owner}</a>
         {f'<div role="button">{switch}</div>' if include_switch else '<span>Go</span>'}
         </section>"""
        other = ("""<section id="other" style="display:flex;width:350px;height:70px">
          <a href="/imposter/">imposter</a><button>Switch</button></section>""" if multiple else "")
        html = f"""<!doctype html><html><body>
        {f'<nav><a href="/{nav}/" aria-label="Profile">Profile</a></nav>' if nav else ""}
        <main><article><a href="/friend/">Friend profile</a><p>Another user</p></article></main>
        <aside style="position:absolute;right:25px;top:80px;width:400px">
          <div style="display:{'none' if hidden else 'block'}">{account}</div>
          {other}
          <h3>Suggested for you</h3>
          <section><a href="/suggested.user/">suggested.user</a><button>Follow</button></section>
        </aside>
        {('<form><input name="password" type="password"></form>' if login else '')}
        </body></html>"""
        self.page.set_content(html, wait_until="domcontentloaded")

    def test_owner_visible_next_to_switch_without_profile_nav(self):
        self.home()
        self.assertEqual(signed_in_handle(self.page), "realmichelduarte")

    def test_spanish_switch_control(self):
        self.home(switch="Cambiar")
        self.assertEqual(signed_in_handle(self.page), "realmichelduarte")

    def test_suggestions_or_hidden_switch_are_not_owner_proof(self):
        for options in ({"include_switch":False}, {"hidden":True}, {"login":True}):
            with self.subTest(options=options):
                self.home(**options)
                self.assertIsNone(signed_in_handle(self.page))

    def test_hidden_password_field_does_not_hide_signed_in_owner(self):
        self.home()
        self.page.locator("body").evaluate("""body => body.insertAdjacentHTML(
          'beforeend', '<form style="display:none"><input name="password" type="password"></form>'
        )""")
        self.assertEqual(signed_in_handle(self.page), "realmichelduarte")

    def test_multiple_switcher_owners_or_nav_conflict_fail_closed(self):
        self.home(multiple=True)
        self.assertIsNone(signed_in_handle(self.page))
        self.home(nav="different.owner")
        self.assertIsNone(signed_in_handle(self.page))

    def test_nav_only_legacy_layout_still_works(self):
        self.home(include_switch=False, nav="realmichelduarte")
        self.assertEqual(signed_in_handle(self.page), "realmichelduarte")

    def test_selected_owner_page_needs_edit_profile_button(self):
        # Offline Instagram URL navigation; no real site is contacted.
        self.page.unroute("**/*")
        def profile_route(route):
            owner = '<button>Edit profile</button>' if owner_has_edit[0] else '<button>Follow</button>'
            route.fulfill(status=200, content_type="text/html", body=(
                '<html><body><header><h2>realmichelduarte</h2>' + owner +
                '</header></body></html>'
            ))
        owner_has_edit=[True]
        self.page.route("https://www.instagram.com/**", profile_route)
        self.assertEqual(verify_selected_owner_profile(self.page, "realmichelduarte"),
                         "realmichelduarte")
        owner_has_edit[0]=False
        self.assertIsNone(verify_selected_owner_profile(self.page, "realmichelduarte"))
        owner_has_edit[0]=True
        self.assertIsNone(verify_selected_owner_profile(self.page, "different.user"))


if __name__ == "__main__":
    unittest.main()
