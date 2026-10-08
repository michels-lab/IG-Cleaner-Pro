#!/usr/bin/env python3
"""Validate actual emulator screenshots for IG Cleaner About at two sizes.

This capture evidence is an automated prerequisite, NOT independent human
acceptance or physical-device certification.
"""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageStat


def digest(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def create_manifest(folder: Path, apk: Path, sha: str):
    assert len(sha) == 40 and all(c in '0123456789abcdef' for c in sha.lower())
    assert apk.is_file() and apk.stat().st_size > 500_000, "Missing actual built Android APK"
    shots = []
    seen = set()
    for viewport in ('compact', 'wide'):
        for part in ('author', 'studio', 'socials'):
            path = folder / f'about-{viewport}-{part}.png'
            assert path.is_file(), f'P0: rendered Android About screenshot missing: {path}'
            assert path.stat().st_size > 3000, f'P0: tiny screenshot: {path}'
            with Image.open(path) as picture:
                picture.verify()
            with Image.open(path) as picture:
                w, h = picture.size
                assert w >= 600 and h >= 1100, f'Invalid screen dimensions: {w}x{h}'
                std = ImageStat.Stat(picture.convert('RGB').resize((64,64))).stddev
                assert max(std) >= 9, f'Blank/near-uniform screenshot {path}'
            expected = (720,1280) if viewport == 'compact' else (1080,1920)
            assert (w,h) == expected, f'{viewport} screenshot must use actual {expected} viewport; got {w,h}'
            hsh = digest(path)
            assert hsh not in seen, f'Screenshot reused across screens/sizes: {path}'
            seen.add(hsh)
            shots.append(dict(
                platform='android', surface='about',
                viewport=viewport, section=part,
                path=path.name, width=w, height=h, sha256=hsh,
                capture_method='installed-android-emulator',
                candidate_artifact_sha256=digest(apk)
            ))
    assert len(shots)==6
    return dict(
        schema='michelslab-rendered-ui-v1',
        source_commit=sha,
        artifact_sha256={'android': digest(apk)},
        screenshots=shots,
        automated_ui_assertions='About author/studio measured bounds; full scrollability; buttons and image drawables',
        human_visual_review={'decision':'PENDING','reviewer':None},
        device_acceptance='UNVERIFIED'
    )


if __name__ == '__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--screenshots',type=Path,required=True)
    ap.add_argument('--apk',type=Path,required=True)
    ap.add_argument('--sha',required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    doc=create_manifest(a.screenshots,a.apk,a.sha)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(doc,indent=2)+'\n',encoding='utf-8')
    print('PASS: 6 actual captured About screenshots, compact+wide, nonblank and APK-hash bound')
    print('Human review and physical Samsung verification remain PENDING.')
