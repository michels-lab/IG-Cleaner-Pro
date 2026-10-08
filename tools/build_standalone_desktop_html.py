#!/usr/bin/env python3
"""Build a genuinely standalone, offline-openable IG Cleaner Pro Desktop HTML.

The source HTML references three files next to it. A plain renamed/copied HTML
would silently lose the author photo, studio lockup and app icon; inline those
exact original bytes as data URLs instead. Preserve the ZIP as a secondary option.
"""
from __future__ import annotations
import argparse
import base64
import hashlib
import json
import mimetypes
import re
from pathlib import Path

REQUIRED_ASSETS = (
    "assets/ig-cleaner-pro/official-app-icon.png",
    "assets/michel_duarte_avatar.jpg",
    "assets/michels-lab/official-lockup.png",
)
ASSET_RE = re.compile(r"""(?P<quote>["'])(?P<path>assets/[^"'<>`]+\.(?:png|jpg|jpeg|webp|svg|gif))(?P=quote)""", re.I)
UNRESOLVED_RE = re.compile(r"""(?:src|href)\s*=\s*["']assets/""", re.I)

def convert(html: str, asset_root: Path) -> tuple[str, dict[str, str]]:
    seen: dict[str, str] = {}
    def repl(m: re.Match[str]) -> str:
        relative=m.group("path")
        if relative.startswith("/") or ".." in Path(relative).parts:
            raise ValueError("Unsafe asset path: " + relative)
        path=(asset_root / relative).resolve()
        if not path.is_relative_to(asset_root.resolve()) or not path.is_file():
            raise FileNotFoundError("Required Desktop asset unavailable: " + relative)
        data=path.read_bytes()
        if not data:
            raise ValueError("Empty Desktop asset: " + relative)
        mime=mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        if mime not in ("image/png","image/jpeg","image/webp","image/svg+xml","image/gif"):
            raise ValueError("Unexpected embedded type: " + mime)
        seen[relative]=hashlib.sha256(data).hexdigest()
        url="data:"+mime+";base64,"+base64.b64encode(data).decode("ascii")
        return m.group("quote")+url+m.group("quote")
    result=ASSET_RE.sub(repl,html)
    if UNRESOLVED_RE.search(result):
        raise ValueError("Standalone HTML contains unresolved relative asset references")
    missing=set(REQUIRED_ASSETS)-set(seen)
    if missing:
        raise ValueError("Desktop branding assets not embedded: "+", ".join(sorted(missing)))
    return result, seen

def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source",type=Path,required=True)
    parser.add_argument("--assets-root",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--version",required=True)
    args=parser.parse_args()
    assert re.fullmatch(r"\d+\.\d+",args.version), "Invalid release version"
    src=args.source.read_text(encoding="utf-8")
    if f"v{args.version}" not in src:
        raise ValueError("Source HTML does not identify requested release version")
    result, evidence=convert(src,args.assets_root)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(result,encoding="utf-8")
    assert args.output.stat().st_size>args.source.stat().st_size,"Assets were not embedded"
    assert 'data:image/png;base64,' in result and 'data:image/jpeg;base64,' in result
    print(json.dumps({"status":"PASS","output":str(args.output),
                      "bytes":args.output.stat().st_size,"embedded":evidence,
                      "sha256":hashlib.sha256(args.output.read_bytes()).hexdigest()},
                     indent=2))
if __name__=="__main__":
    main()
