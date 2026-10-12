import csv
from pathlib import Path
import tempfile
import unittest
from tools.profile_counts_instagram import (
    user_from_href, own_profile_from_anchors,
    write_following_cache, read_following_cache,
    expected_following_count, reconcile_following_discovery
)

from tools.profile_counts_robot import (
    parse_number, parse_profile_counts, read_queue, read_results, save_results,
    valid_username,
)

class InstagramVisibleDiscoveryTests(unittest.TestCase):
    def test_profile_identity_must_come_from_labeled_nav(self):
        self.assertEqual(own_profile_from_anchors([
            {"href":"/random/", "text":"Photo by"},
            {"href":"/myinstagram/", "aria":"Perfil"},
        ]),"myinstagram")
        self.assertIsNone(own_profile_from_anchors([
            {"href":"/random/", "text":"Photo by"}
        ]))
        self.assertIsNone(own_profile_from_anchors([
            {"href":"/user1/", "aria":"Profile"},
            {"href":"/user2/", "aria":"Profile"}
        ]))

    def test_following_urls_reject_non_profile_paths(self):
        self.assertEqual(user_from_href("/friend.user/"),"friend.user")
        for value in ("/p/photo/", "/explore/", "/direct/inbox/",
                      "/accounts/login/", "https://example.org/not-instagram/"):
            self.assertIsNone(user_from_href(value))

    def test_visible_following_exact_count_required_for_completion(self):
        self.assertEqual(expected_following_count("Following 11,869"), 11869)
        self.assertEqual(expected_following_count("1.234 seguidos"), 1234)
        self.assertEqual(expected_following_count("Following"), None)
        self.assertEqual(expected_following_count("11.8K Following"), None)
        self.assertEqual(expected_following_count("12,3 mil seguidos"), None)

    def test_partial_following_resume_preserves_cached_checkpoint(self):
        previous = ["old.friend", "still.friend", "@still.friend"]
        observed = ["still.friend", "new.friend"]
        self.assertEqual(reconcile_following_discovery(previous, observed, False),
                         ["old.friend", "still.friend", "new.friend"])
        self.assertEqual(reconcile_following_discovery(previous, observed, True),
                         ["still.friend", "new.friend"])
        self.assertEqual(reconcile_following_discovery(previous, [], False),
                         ["old.friend", "still.friend"])
        self.assertEqual(reconcile_following_discovery(previous, [], True), [])

    def test_following_cache_keeps_instagram_separate(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/"following.json"
            write_following_cache(path,"owner1",["one","one","@two"],False)
            self.assertEqual(read_following_cache(path,"owner1"),["one","two"])
            self.assertEqual(read_following_cache(path,"owner2"),[])


class ProfileCountsRobotTests(unittest.TestCase):
    def test_visible_meta_english(self):
        self.assertEqual(parse_profile_counts(
            "999 Posts, 1,234 Followers, 567 Following - See Instagram photos"), (1234, 567, False))
    def test_visible_header_spanish(self):
        self.assertEqual(parse_profile_counts("123 publicaciones\n1.234 seguidores\n56 seguidos"), (1234, 56, False))
    def test_abbreviations_are_flagged_approximate(self):
        self.assertEqual(parse_profile_counts("12.3K followers and 3.5K following"), (12300, 3500, True))
        self.assertEqual(parse_profile_counts("12,3 mil seguidores, 222 seguidos"), (12300, 222, True))
    def test_missing_is_not_fake_zero(self):
        self.assertIsNone(parse_profile_counts("Posts only"))
        self.assertIsNone(parse_profile_counts("Private account • Follow to see photos"))
        self.assertEqual(parse_profile_counts("0 followers, 0 following"), (0, 0, False))
    def test_number_rejects_invalid(self):
        self.assertIsNone(parse_number("approx 33"))
        self.assertEqual(parse_number("1.234"), (1234, False))
    def test_input_validation(self):
        self.assertEqual(valid_username("@real.user"), "real.user")
        self.assertEqual(valid_username("https://www.instagram.com/Some_Name/"), "some_name")
        self.assertIsNone(valid_username("https://example.com/Some_Name"))
        self.assertIsNone(valid_username("../../private"))
    def test_queue_dedup_and_atomic_resume(self):
        with tempfile.TemporaryDirectory() as folder:
            base=Path(folder); src=base/"queue.csv"; dest=base/"result.csv"
            src.write_text("username,profile_url\none,https://www.instagram.com/one/\nONE,\n@two,\n",encoding="utf-8")
            self.assertEqual(read_queue(src), ["one","two"])
            record={"username":"one","followers":"23","following":"45",
                    "checked_at":"2026-10-11T00:00:00+00:00","source":"visible","status":"ok","approximate":"false"}
            save_results(dest,{"one":record})
            self.assertEqual(read_results(dest)["one"]["followers"],"23")
            self.assertFalse((base/"result.csv.tmp").exists())

if __name__ == "__main__":
    unittest.main()
