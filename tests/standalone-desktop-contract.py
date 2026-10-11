#!/usr/bin/env python3
"""Enforce a directly downloadable, offline-ready Desktop HTML release."""
from pathlib import Path
import importlib.util
import json
import tempfile
import base64

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("single_html",ROOT/"tools/build_standalone_desktop_html.py")
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
assets=ROOT/"desktop"
src=ROOT/"desktop/ig_cleaner_pro_v120_27_synced_companion.html"
manifest=json.loads((ROOT/"release/distribution-manifest.json").read_text(encoding="utf-8"))
desktop=manifest["channels"]["desktop"]
assert desktop["primaryArtifactTemplate"]=="IG-Cleaner-Pro-Desktop-v{version}.html"
assert desktop["artifactTemplate"]=="IG-Cleaner-Pro-Desktop-v{version}.zip"
assert desktop["standaloneOffline"] is True
assert desktop["primaryFormat"]=="html"
assert desktop["zipSecondary"] is True
converted,evidence=module.convert(src.read_text(encoding="utf-8"),assets)
assert len(evidence)==3 and len(converted)>len(src.read_text(encoding="utf-8"))
assert converted.count("data:image/")>=3
assert 'href="assets/' not in converted and 'src="assets/' not in converted
for v in evidence.values():
    assert len(v)==64

with tempfile.TemporaryDirectory() as temp:
    root=Path(temp)
    for rel in module.REQUIRED_ASSETS:
        p=root/rel
        p.parent.mkdir(parents=True,exist_ok=True)
        p.write_bytes(b"test-asset-binary")
    fake="v120.39 "+' '.join(f'<img src="{rel}">' for rel in module.REQUIRED_ASSETS)
    html,embed=module.convert(fake,root)
    assert len(embed)==3 and html.count("data:image/")==3
    (root/module.REQUIRED_ASSETS[0]).unlink()
    try:
        module.convert(fake,root)
        raise AssertionError("Missing canonical image must block standalone release")
    except FileNotFoundError:
        pass

workflow=(ROOT/".github/workflows/release.yml").read_text(encoding="utf-8")
for token in ("build_standalone_desktop_html.py","desktop_html_artifact","--assets-root package",
              'gh release view', 'SHA256SUMS.txt'):
    assert token in workflow, f"Publisher not configured for HTML first-class artifact: {token}"
print("PASS: Desktop HTML embeds all canonical assets and direct HTML release is mandatory.")
