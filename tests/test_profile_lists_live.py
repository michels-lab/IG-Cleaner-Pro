"""Offline tests for owner-opt-in read-only live list paging.

No Instagram credentials, network, or relationship-changing calls.
"""
import unittest
from unittest.mock import Mock, patch

try:
    from tools.profile_lists_live import read_live_friendship_list, LiveListsUnavailable
except ImportError:
    from profile_lists_live import read_live_friendship_list, LiveListsUnavailable


class LiveFriendshipListTests(unittest.TestCase):
    def page(self, packets, *, url="https://www.instagram.com/"):
        page = Mock()
        page.url = url
        page.evaluate.side_effect = packets
        return page

    def scan(self, page, relation="followers", **kwargs):
        with patch("tools.profile_lists_live.signed_in_handle", return_value="my.profile"), \
             patch("tools.profile_lists_live.challenge_detected", return_value=False):
            return read_live_friendship_list(page, "my.profile", relation, **kwargs)

    def test_complete_followers_cursor_pages_are_read_only_and_deduplicated(self):
        page = self.page([
            {"usernames":["other.person","old.friend"],"next":"cursor-2","has_more":True},
            {"usernames":["other.person","another"],"next":None,"has_more":False}
        ])
        observed = self.scan(page)
        self.assertEqual(observed, frozenset(("other.person","old.friend","another")))
        self.assertEqual(page.evaluate.call_count,2)
        self.assertEqual(page.wait_for_timeout.call_count,1)
        self.assertEqual(page.evaluate.call_args_list[0].args[1]["kind"],"followers")
        self.assertEqual(page.evaluate.call_args_list[1].args[1]["cursor"],"cursor-2")

    def test_following_list_is_independent_from_profile_counts(self):
        page = self.page([{"usernames":["target.user"],"next":None}])
        self.assertEqual(self.scan(page,"following"),frozenset(("target.user",)))
        self.assertEqual(page.evaluate.call_args.args[1]["kind"],"following")

    def test_incomplete_and_blocked_lists_never_yield_false_nonfollowbacks(self):
        cases=[
            [{"error":"http_429"}],
            [{"error":"owner_id_not_available"}],
            [{"usernames":["a"],"next":None,"has_more":True}],
            [{"usernames":["a"],"next":"loop"},{"usernames":["b"],"next":"loop"}],
            [{"usernames":["a"],"next":"next"}],
            [{"usernames":[None],"next":None}],
            [{"usernames":["a"],"next":None,"has_more":False,"status":"unexpected"}],
        ]
        for packets in cases:
            with self.subTest(packets=packets):
                with self.assertRaises(LiveListsUnavailable):
                    self.scan(self.page(packets),max_pages=1 if len(packets)==1 and packets[0].get("next") else 250)

    def test_wrong_active_owner_never_fetches_a_single_page(self):
        page=self.page([{"usernames":[],"next":None}])
        with patch("tools.profile_lists_live.signed_in_handle",return_value="another.account"), \
             patch("tools.profile_lists_live.challenge_detected",return_value=False):
            with self.assertRaises(LiveListsUnavailable):
                read_live_friendship_list(page,"my.profile","followers")
        self.assertEqual(page.evaluate.call_count,0)

    def test_security_challenge_never_fetches_a_page(self):
        page=self.page([{"usernames":[],"next":None}])
        with patch("tools.profile_lists_live.signed_in_handle",return_value="my.profile"), \
             patch("tools.profile_lists_live.challenge_detected",return_value=True):
            with self.assertRaises(LiveListsUnavailable):
                read_live_friendship_list(page,"my.profile","following")
        self.assertEqual(page.evaluate.call_count,0)

    def test_invalid_relation_and_owner_rejected(self):
        page=self.page([])
        for owner,kind in [("other","unfollow"),("wrong handle","followers")]:
            with self.assertRaises(ValueError):
                read_live_friendship_list(page,owner,kind)
        self.assertEqual(page.evaluate.call_count,0)


if __name__=="__main__":
    unittest.main()
