"""Regression matrix for browser-local read-only Instagram structured lookup.

No real Instagram connection, session, profile, cookie, export or mutation.
The optional Node harness runs the STATIC browser JS with a fake fetch.
"""
from pathlib import Path
from unittest import TestCase, main
from unittest.mock import Mock
import json
import shutil
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from ig_structured_probe import (
    inspect_structured_following, _READ_ONLY_FOLLOWING_LOOKUP,
)


class ReadOnlyStructuredTransport(TestCase):
    def test_unverified_owner_never_invokes_page_javascript(self):
        page = Mock(url="https://www.instagram.com/sample.person/")
        self.assertEqual(
            inspect_structured_following(page, "sample.person", owner_verified=False),
            "STRUCTURED_UNAVAILABLE",
        )
        page.evaluate.assert_not_called()

    def test_wrong_origin_or_target_never_invokes_page_javascript(self):
        for url in (
            "https://other.example/sample.person/",
            "http://www.instagram.com/sample.person/",
            "https://www.instagram.com/different.person/",
            "https://www.instagram.com/accounts/login/",
        ):
            with self.subTest(url=url):
                page = Mock(url=url)
                self.assertEqual(
                    inspect_structured_following(page, "sample.person", owner_verified=True),
                    "STRUCTURED_UNAVAILABLE",
                )
                page.evaluate.assert_not_called()

    def test_bounded_codes_and_static_source(self):
        page = Mock(url="https://www.instagram.com/sample.person/")
        for input_value, expected in (
            ({"code": "FOLLOWING_STRUCTURED"}, "FOLLOWING_STRUCTURED"),
            ({"code": "STRUCTURED_RATE_LIMITED"}, "STRUCTURED_RATE_LIMITED"),
            ({"code": "OTHER", "secret": "something"}, "STRUCTURED_UNAVAILABLE"),
            ("invalid", "STRUCTURED_UNAVAILABLE"),
        ):
            page.evaluate.return_value = input_value
            self.assertEqual(
                inspect_structured_following(page, "sample.person", owner_verified=True),
                expected,
            )
        sent = page.evaluate.call_args
        self.assertEqual(sent.args[1], {"username": "sample.person"})
        self.assertIn("async ({username}) =>", sent.args[0])
        self.assertIn("method: 'GET'", sent.args[0])
        self.assertIn("credentials: 'same-origin'", sent.args[0])
        self.assertIn("redirect: 'error'", sent.args[0])
        self.assertNotIn("method: 'POST'", sent.args[0])
        self.assertNotIn("/api/graphql", sent.args[0])
        self.assertNotIn("return {code: 'FOLLOWING_STRUCTURED', id:", sent.args[0])

    def test_one_real_javascript_execution_using_fake_network_only(self):
        if not shutil.which("node"):
            self.skipTest("Node runtime unavailable for JavaScript contract fixture")
        cases = [
            ([{"username": "sample.person", "pk_id": "123"}],
             200, "FOLLOWING_STRUCTURED"),
            ([{"username": "another.person", "pk_id": "123"}],
             200, "STRUCTURED_UNAVAILABLE"),
            ([{"username": "sample.person", "pk_id": "not-numeric"}],
             200, "STRUCTURED_UNAVAILABLE"),
            ([{"username": "sample.person", "pk_id": "123"},
              {"username": "sample.person", "pk_id": "999"}],
             200, "STRUCTURED_UNAVAILABLE"),
            ([], 429, "STRUCTURED_RATE_LIMITED"),
        ]
        for users, status, expected in cases:
            with self.subTest(expected=expected, users=users):
                script = """
const source = %s;
const users = %s;
const status = %s;
let sent = [];
globalThis.window = {location:{hostname:'www.instagram.com', protocol:'https:'}};
globalThis.location = {origin:'https://www.instagram.com'};
globalThis.document = {cookie:'ds_user_id=99999; csrftoken=FIXTURE_SECRET'};
globalThis.fetch = async (url, opts) => {
  sent.push({url, method:opts.method, credentials:opts.credentials,
             csrf:opts.headers['X-CSRFToken'], body:opts.body});
  return {status, ok:status===200, json:async()=>({users})};
};
(async () => {
  const lookup = eval('(' + source + ')');
  const result = await lookup({username:'sample.person'});
  process.stdout.write(JSON.stringify({result, sent}));
})().catch(error => {process.stderr.write(String(error)); process.exit(3)});
""" % (json.dumps(_READ_ONLY_FOLLOWING_LOOKUP), json.dumps(users), status)
                p = subprocess.run(
                    ["node", "-e", script], capture_output=True, text=True,
                    timeout=8, check=True,
                )
                result = json.loads(p.stdout)
                self.assertEqual(result["result"], {"code": expected})
                self.assertEqual(len(result["sent"]), 1)
                request = result["sent"][0]
                self.assertEqual(request["method"], "GET")
                self.assertEqual(request["credentials"], "same-origin")
                self.assertEqual(request["csrf"], "FIXTURE_SECRET")
                self.assertNotIn("body", request)
                self.assertTrue(request["url"].startswith(
                    "https://www.instagram.com/api/v1/friendships/99999/following/?"
                ))
                # The browser-only secret must never appear in a diagnostic.
                self.assertNotIn("FIXTURE_SECRET", json.dumps(result["result"]))


if __name__ == "__main__":
    main()
