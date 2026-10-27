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
        page = self.page([{"usernames":["target.user"],"next":None,"has_more":False}])
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
            [{"usernames":["a"],"next":None}],
            [{"usernames":["a"],"next":"x","has_more":False}],
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


    def test_bulk_membership_extends_beyond_250_api_pages_without_opening_profiles(self):
        # Instagram sometimes returns far fewer members than "count=200".
        # 275 JSON pages are not 275 individual profile visits.
        packets=[
            {"members":[{"id":str(100000+i),"username":"member"+str(i)}],
             "next":"page-"+str(i+1) if i<274 else None,
             "has_more":i<274}
            for i in range(275)
        ]
        page=self.page(packets)
        seen=[]
        with patch("tools.profile_lists_live.signed_in_handle",return_value="my.profile"), \
             patch("tools.profile_lists_live.challenge_detected",return_value=False):
            identities=read_live_friendship_list(
                page,"my.profile","following",identities=True,
                on_progress=lambda kind,count:seen.append((kind,count)))
        self.assertEqual(len(identities),275)
        self.assertEqual(identities["100274"],"member274")
        self.assertEqual(page.evaluate.call_count,275)
        self.assertEqual(seen[-1],("following",275))
        self.assertEqual(page.wait_for_timeout.call_count,274)
        page.goto.assert_not_called()
        js=page.evaluate.call_args_list[0].args[0]
        self.assertIn("/api/v1/friendships/",js)
        self.assertIn("method:'GET'",js)
        self.assertNotIn("graphql",js.casefold())
        self.assertNotIn("/users/",js)

    def test_nonterminal_legacy_250_page_budget_no_longer_truncates_scan(self):
        page=self.page([
            {"members":[{"id":str(i+1),"username":"person"+str(i)}],
             "next":"cursor"+str(i+1),"has_more":True}
            for i in range(251)
        ])
        with self.assertRaises(LiveListsUnavailable) as error:
            self.scan(page,identities=True,max_pages=251)
        self.assertIn("251 pages",str(error.exception))
        self.assertIn("251 unique",str(error.exception))
        self.assertEqual(page.evaluate.call_count,251)

    def test_stalled_cursor_pages_fail_before_a_long_infinite_bulk_scan(self):
        page=self.page([
            {"members":[{"id":"100","username":"same.person"}],
             "next":"c"+str(i+1),"has_more":True}
            for i in range(50)
        ])
        with self.assertRaisesRegex(LiveListsUnavailable,"stopped yielding"):
            self.scan(page,identities=True)
        self.assertLessEqual(page.evaluate.call_count,10)

    def test_stable_numeric_ids_are_required_for_member_comparison(self):
        bad=[
            {"members":[{"id":None,"username":"person"}],"next":None,"has_more":False},
            {"members":[{"id":"opaque","username":"person"}],"next":None,"has_more":False},
            {"members":[{"id":"1","username":"person"},{"id":"2","username":"person"}],
             "next":None,"has_more":False},
        ]
        for packet in bad:
            with self.subTest(packet=packet),self.assertRaises(LiveListsUnavailable):
                self.scan(self.page([packet]),identities=True)

if __name__=="__main__":
    unittest.main()
