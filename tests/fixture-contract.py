#!/usr/bin/env python3
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
fixture = ROOT / "tests" / "fixtures" / "instagram-export-sample"
assert fixture.is_dir(), "Sanitized Instagram fixture directory is missing."

files = [p for p in fixture.rglob("*") if p.is_file()]
assert len(files) == 13, f"Expected 13 sanitized fixture files, found {len(files)}."

lowered = [str(p.relative_to(fixture)).lower() for p in files]
assert any("following.json" in n for n in lowered), "Fixture must exercise following import."
assert sum(p.name.startswith("followers_") and p.suffix.lower() == ".json" for p in files) == 3, "Fixture must contain three followers parts."
assert any("pending_follow_requests" in n for n in lowered), "Fixture must exercise pending requests."

parsed_json = 0
html_files = 0
for path in files:
    data = path.read_bytes()
    if path.suffix.lower() == ".json":
        json.loads(data.decode("utf-8"))
        parsed_json += 1
    elif path.suffix.lower() in {".html", ".htm"}:
        text = data.decode("utf-8", errors="strict")
        assert "instagram.com" in text.lower(), f"Unexpected HTML fixture: {path}"
        html_files += 1

assert parsed_json == 12, f"Expected 12 valid JSON fixture files, found {parsed_json}."
assert html_files == 1, f"Expected one HTML fixture, found {html_files}."

following = json.loads((fixture / "connections/followers_and_following/following.json").read_text())
assert len(following["relationships_following"]) == 3

followers = []
for i in range(1, 4):
    followers += json.loads((fixture / f"connections/followers_and_following/followers_{i}.json").read_text())
assert len(followers) == 5

pending = json.loads((fixture / "connections/followers_and_following/pending_follow_requests.json").read_text())
assert len(pending["relationships_follow_requests_sent"]) == 2

print("Fixture contract passed: 13 files; Following 3; Followers 5; Pending 2.")
