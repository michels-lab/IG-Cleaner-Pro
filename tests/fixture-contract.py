#!/usr/bin/env python3
import json
import pathlib
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
fixture = ROOT / "tests" / "fixtures" / "instagram-export-sample.zip"
assert fixture.exists() and fixture.stat().st_size > 1000, "Sanitized Instagram fixture is missing or empty."

with zipfile.ZipFile(fixture) as z:
    names = z.namelist()
    assert names, "Fixture ZIP is empty."
    lowered = [n.lower() for n in names]
    assert any("following" in n for n in lowered), "Fixture must exercise following import."
    assert any("followers" in n for n in lowered), "Fixture must exercise followers import."
    assert any("pending" in n or "request" in n for n in lowered), "Fixture must exercise pending/request import."

    parsed_json = 0
    html_files = 0
    for name in names:
        data = z.read(name)
        if name.lower().endswith(".json"):
            json.loads(data.decode("utf-8"))
            parsed_json += 1
        elif name.lower().endswith((".html", ".htm")):
            text = data.decode("utf-8", errors="strict")
            assert "instagram" in text.lower() or "profile" in text.lower(), f"Unexpected HTML fixture: {name}"
            html_files += 1

    assert parsed_json > 0, "Fixture must contain at least one valid JSON document."
    assert html_files > 0, "Fixture must contain at least one HTML export."

print(f"Fixture contract passed: {len(names)} files, {parsed_json} JSON, {html_files} HTML.")
