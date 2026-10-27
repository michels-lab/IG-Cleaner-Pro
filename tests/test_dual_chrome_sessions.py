"""Regression: Chrome A and B must never reuse the same Instagram browser state."""
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from dual_chrome_sessions import DualChromeSessions


class DualChromeSessionTests(unittest.TestCase):
    OWNER = "u_abcdef_19"
    FIRST = "ig_alice_1234567"
    SECOND = "ig_bob_12345678"

    def request(self, **overrides):
        data = {"owner": self.OWNER,
                "primary": {"account": self.FIRST, "expected_handle": "alice.id"},
                "secondary": {"account": self.SECOND, "expected_handle": "bob.id"},
                "read_only_consent": True,
                "confirmation": "dual-chrome:" + self.FIRST + ":" + self.SECOND}
        data.update(overrides)
        return data

    def test_two_actual_distinct_persistent_user_data_directories(self):
        calls = []
        with TemporaryDirectory() as temp:
            root = Path(temp)
            launcher = lambda args: calls.append(args)
            duo = DualChromeSessions(root, chrome_locator=lambda: Path("chrome.exe"),
                                     launcher=launcher)
            state = duo.open_pair(self.request())
            self.assertEqual(state["windows_requested"], 2)
            self.assertTrue(state["distinct_chrome_profiles"])
            self.assertFalse(state["actions_enabled"])
            self.assertEqual(len(calls), 2)
            profiles = [next(a for a in argv if a.startswith("--user-data-dir="))
                        for argv in calls]
            self.assertNotEqual(profiles[0], profiles[1])
            self.assertNotIn("instagram-browser", profiles[0])
            self.assertNotIn("instagram-browser", profiles[1])
            for command in calls:
                self.assertIn("--new-window", command)
                self.assertEqual(command[-1], "https://www.instagram.com/")
                self.assertFalse(any("cookie" in a.lower() for a in command))
            self.assertEqual(duo.directory(self.OWNER,self.FIRST),
                             duo.directory(self.OWNER,self.FIRST),
                             "Restart must reuse the same owner's own Chrome profile.")
            self.assertNotEqual(duo.directory(self.OWNER,self.FIRST),
                                duo.directory("u_different_19",self.FIRST),
                                "Different app owner must not inherit Chrome cookies.")
            duo.open_pair(self.request())
            self.assertEqual(profiles[0],
                next(a for a in calls[2] if a.startswith("--user-data-dir=")))

    def test_wrong_workspace_or_missing_consent_launches_nothing(self):
        calls = []
        with TemporaryDirectory() as temp:
            duo = DualChromeSessions(temp,chrome_locator=lambda: Path("chrome.exe"),
                                     launcher=lambda args: calls.append(args))
            invalid = [
                self.request(owner="signed_out"),
                self.request(primary={"account":self.SECOND,"expected_handle":"alice.id"}),
                self.request(secondary={"account":self.SECOND,"expected_handle":"alice.id"}),
                self.request(secondary={"account":"../../browser","expected_handle":"bob.id"}),
                self.request(primary={"account":self.FIRST,"expected_handle":"https://evil.test"}),
                self.request(confirmation="wrong"),
                self.request(read_only_consent=False),
            ]
            for request in invalid:
                with self.subTest(request=request), self.assertRaises(ValueError):
                    duo.open_pair(request)
            self.assertEqual(calls,[], "Invalid requests must never launch Chrome.")

    def test_failed_second_window_is_not_claimed_as_both_launched(self):
        with TemporaryDirectory() as temp:
            calls=[]
            def launcher(args):
                calls.append(args)
                if len(calls)==2: raise OSError("Chrome process failed")
            duo=DualChromeSessions(temp,chrome_locator=lambda:Path("chrome.exe"),
                                   launcher=launcher)
            with self.assertRaisesRegex(ValueError,"window B"):
                duo.open_pair(self.request())
            self.assertEqual(len(calls),2)


if __name__=="__main__":
    unittest.main()
