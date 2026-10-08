#!/usr/bin/env python3
"""Fail closed unless the exact release commit has genuine Desktop browser screenshots."""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageStat

def digest(file:Path)->str:
    return hashlib.sha256(file.read_bytes()).hexdigest()

def verify(root:Path, sha:str, html:Path):
    manifest = json.loads((root/"manifest.json").read_text(encoding="utf-8"))
    assert manifest.get("schema") == "igc-desktop-runtime-visual-v1"
    assert manifest.get("source_commit") == sha, "Desktop screenshot source SHA mismatch"
    assert digest(html) == manifest.get("html_sha256"), "Screenshot HTML differs from release Desktop HTML"
    shots = manifest.get("screenshots")
    assert len(shots)==6, "Missing real Home/About/Desktop screenshot coverage"
    expected={(surface,viewport,section) for viewport in ("compact","wide")
              for surface,section in (("home","initial"),("about","initial"),("about","socials"))}
    visited=set()
    seen={}
    for shot in shots:
        key=(shot.get("surface"),shot.get("viewport"),shot.get("section"))
        assert key in expected and key not in visited, f"Missing/duplicate runtime screenshot: {key}"
        visited.add(key)
        assert shot.get("capture_method")=="running-browser", "Static image passed instead of runtime capture"
        p=(root/shot.get("path","")).resolve()
        assert p.is_relative_to(root.resolve()), "Screenshot path traversal rejected"
        assert p.exists() and p.stat().st_size > 3000, "Screenshot missing or suspiciously tiny"
        assert digest(p)==shot.get("sha256"), "Screenshot tampered or from another run"
        with Image.open(p) as raw: raw.verify()
        with Image.open(p) as im:
            size=im.size
            expected_dim=(390,844) if shot["viewport"]=="compact" else (1360,900)
            assert size==expected_dim, f"Viewport mismatch: {size}"
            assert size==(shot["width"],shot["height"])
            assert max(ImageStat.Stat(im.convert("RGB").resize((64,64))).stddev)>9, "Blank screenshot"
        old=seen.get(shot["sha256"])
        assert old is None or old == shot["viewport"], "Reused screenshot across screen sizes"
        seen[shot["sha256"]] = shot["viewport"]
    assert visited==expected
    print("PASS: exact-commit Desktop Home/About in real browser, two viewport classes and six validated PNGs")

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--artifact",type=Path,required=True)
    ap.add_argument("--html",type=Path,required=True)
    ap.add_argument("--sha",required=True)
    args=ap.parse_args()
    verify(args.artifact,args.sha,args.html)
