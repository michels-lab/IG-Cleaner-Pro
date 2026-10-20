"""GRANADA #13: corrupt historical CSV cannot be silently collapsed or rewritten."""
import csv
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

from tools.profile_counts_robot import FIELDS, read_results, save_results
from tools.profile_counts_bridge import Collector


def row(name="owner.one", followers="23", following="16", status="ok"):
    return dict(username=name, followers=followers, following=following,
                checked_at="2026-10-18T12:00:00Z",
                source="instagram_visible_profile_browser",
                status=status, approximate="false")


def csv_text(headers, rows):
    from io import StringIO
    file = StringIO(newline="")
    writer = csv.writer(file, lineterminator="\n")
    writer.writerow(headers)
    writer.writerows(rows)
    return file.getvalue()


class CsvRecoveryFailClosedTests(unittest.TestCase):
    def assert_bad_preserved(self, content, match="CSV|profile"):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "results.csv"
            path.write_bytes(content.encode("utf-8"))
            original = path.read_bytes()
            with self.assertRaisesRegex(ValueError, match):
                read_results(path)
            self.assertEqual(path.read_bytes(), original)
            self.assertFalse(path.with_suffix(".csv.tmp").exists())

    def test_duplicate_rows_even_if_identical_must_not_erase_historical_evidence(self):
        saved = row()
        duplicate = row(followers="99")
        headers = list(FIELDS)
        self.assert_bad_preserved(csv_text(headers,
            [[saved[h] for h in headers], [duplicate[h] for h in headers]]),
            "duplicate profile")
        alias = row(name="@OWNER.ONE")
        self.assert_bad_preserved(csv_text(headers,
            [[saved[h] for h in headers], [alias[h] for h in headers]]),
            "duplicate profile")
        same = row()
        self.assert_bad_preserved(csv_text(headers,
            [[saved[h] for h in headers], [same[h] for h in headers]]),
            "duplicate profile")

    def test_unknown_duplicate_or_missing_headers_fail_before_rewrite(self):
        saved = row()
        base = list(FIELDS)
        for headers, values in [
            (base + ["private_owner_note"], [saved[k] for k in base] + ["keep"]),
            (base + ["username"], [saved[k] for k in base] + ["different"]),
            ([h for h in base if h != "following"],
             [saved[h] for h in base if h != "following"]),
            (["not_a_profile", "status"], ["foo", "ok"]),
        ]:
            with self.subTest(headers=headers):
                self.assert_bad_preserved(csv_text(headers, [values]), "CSV columns")

    def test_partial_or_surplus_row_and_malformed_syntax_fail_closed(self):
        headers = list(FIELDS)
        good = row()
        values = [good[h] for h in headers]
        for records in (
            [values, values[:3]],
            [values + ["surplus"]],
            [values, values + ["extra", "private"]],
            [["../unsafe", *values[1:]]],
        ):
            with self.subTest(records=records):
                self.assert_bad_preserved(csv_text(headers, records))
        self.assert_bad_preserved(",".join(headers) + "\nowner.one,\"unterminated", "malformed CSV")
        self.assert_bad_preserved("", "CSV columns")

    def test_valid_bom_and_legacy_optional_columns_remain_compatible(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "results.csv"
            saved = row(name="OWNER.ONE")
            keys = ["username", "followers", "following", "checked_at", "status"]
            payload = csv_text(keys, [[saved[k] for k in keys]])
            path.write_bytes(b"\xef\xbb\xbf" + payload.encode("utf-8"))
            before = path.read_bytes()
            loaded = read_results(path)
            self.assertEqual(set(loaded), {"owner.one"})
            self.assertEqual(loaded["owner.one"]["followers"], "23")
            self.assertEqual(loaded["owner.one"]["username"], "OWNER.ONE")
            self.assertEqual(path.read_bytes(), before)

            values = {
                "owner.one": row(),
                "second.two": row(name="second.two", followers="", following="", status="unavailable"),
            }
            out = Path(folder) / "new.csv"
            save_results(out, values)
            self.assertEqual(set(read_results(out)), set(values))
            self.assertEqual(read_results(out)["second.two"]["followers"], "")

    def test_installed_windows_bridge_cannot_start_with_duplicate_result_ledger(self):
        with tempfile.TemporaryDirectory() as folder:
            c = Collector(Path(folder) / "results", Path(folder) / "session")
            c.owner, c.account = "owner-A", "instagram-A"
            path = c.result_path()
            path.parent.mkdir(parents=True, exist_ok=True)
            saved = row()
            bad = csv_text(FIELDS, [[saved[k] for k in FIELDS]] * 2)
            path.write_text(bad, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate profile"):
                c.start(dict(owner=c.owner, account=c.account,
                             usernames=["owner.one"]), load_only=True)
            self.assertEqual(path.read_text(encoding="utf-8"), bad)
            self.assertFalse(path.with_suffix(".csv.tmp").exists())
            self.assertFalse(c.worker and c.worker.is_alive())


if __name__ == "__main__":
    unittest.main()
