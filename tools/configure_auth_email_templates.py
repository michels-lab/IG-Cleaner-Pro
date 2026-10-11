#!/usr/bin/env python3
"""Manage only IG Cleaner's OTP email templates in hosted Supabase Auth.

No database/user mutations. Does not change SMTP, Site URL or allowed redirects.
Requires a private Supabase management access token in the environment for
remote operations. The --local check needs no credentials/network.
"""
import argparse
import json
import os
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
PROJECT_REF = "ilmztedebwdzgnlrvwxy"
API = "https://api.supabase.com/v1/projects/" + PROJECT_REF + "/config/auth"

TEMPLATES = {
    "mailer_subjects_confirmation": "Your IG Cleaner verification code",
    "mailer_templates_confirmation_content": (
        ROOT / "supabase/email-templates/confirmation.html"
    ),
    "mailer_subjects_magic_link": "Your IG Cleaner verification code",
    "mailer_templates_magic_link_content": (
        ROOT / "supabase/email-templates/magic_link.html"
    ),
}


def desired():
    payload = {}
    for key, value in TEMPLATES.items():
        payload[key] = value.read_text(encoding="utf-8") if isinstance(value, Path) else value
    for key in ("mailer_templates_confirmation_content", "mailer_templates_magic_link_content"):
        html = payload[key]
        if html.count("{{ .Token }}") != 1:
            raise ValueError(key + " must contain exactly one OTP token")
        if "{{ .ConfirmationURL }}" in html or "localhost:3000" in html:
            raise ValueError(key + " must not contain magic link or localhost fallback")
        if "Michel's Lab" not in html or "Instagram Cleaner Pro" not in html:
            raise ValueError(key + " lacks approved sender/brand identity")
    return payload


def request(method, payload=None):
    token = os.environ.get("SUPABASE_ACCESS_TOKEN", "").strip()
    if not token:
        raise RuntimeError(
            "SUPABASE_ACCESS_TOKEN is required for remote operations. "
            "Set it privately outside the repository or paste templates in the Supabase Dashboard."
        )
    headers = {"Authorization": "Bearer " + token, "Accept": "application/json"}
    body = None
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    try:
        with urlopen(Request(API, headers=headers, data=body, method=method), timeout=25) as resp:
            data = resp.read().decode("utf-8")
            return json.loads(data) if data else {}
    except HTTPError as error:
        # Do NOT display provider error bodies: they may contain configuration.
        raise RuntimeError(f"Supabase management API returned HTTP {error.code}") from None
    except URLError:
        raise RuntimeError("Could not reach Supabase management API") from None


def main():
    parser = argparse.ArgumentParser(description="IG Cleaner email template configuration")
    parser.add_argument(
        "mode", choices=["local", "status", "apply"],
        help="local checks files, status compares production config, apply updates only four template fields"
    )
    parser.add_argument(
        "--confirm-project", default="",
        help="required for apply: exact Supabase project reference"
    )
    args = parser.parse_args()
    required = desired()
    if args.mode == "local":
        print("PASS: both length-agnostic branded OTP email templates are locally valid")
        return
    if args.mode == "apply":
        if args.confirm_project != PROJECT_REF:
            parser.error("Refusing production changes: --confirm-project must equal " + PROJECT_REF)
        existing = request("GET")
        mismatched = sorted(key for key, value in required.items() if existing.get(key) != value)
        if not mismatched:
            print("Already configured: four fields match the canonical templates")
            return
        request("PATCH", {key: required[key] for key in mismatched})
        print("Updated Supabase email template fields: " + ", ".join(mismatched))
    current = request("GET")
    mismatched = sorted(key for key, value in required.items() if current.get(key) != value)
    if mismatched:
        print("NOT CONFIGURED: fields still differ: " + ", ".join(mismatched))
        raise SystemExit(2)
    print("VERIFIED: both Auth email templates are live and contain length-agnostic OTP codes")
    print("SMTP sender name/address and Site URL are separate settings; not modified here.")


if __name__ == "__main__":
    main()
