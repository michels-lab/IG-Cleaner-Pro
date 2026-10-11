#!/usr/bin/env python3
"""Offline regression: emailed sign-up and recovery must contain code, not link."""
from pathlib import Path
import importlib.util
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / "tools/configure_auth_email_templates.py"
spec = importlib.util.spec_from_file_location("igc_auth_email", source)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

payload = module.desired()
assert set(payload) == {
    "mailer_subjects_confirmation",
    "mailer_templates_confirmation_content",
    "mailer_subjects_magic_link",
    "mailer_templates_magic_link_content",
}, "Do not change SMTP keys or unrelated Auth options from the template helper"
for key, content in payload.items():
    if key.endswith("_content"):
        assert content.count("{{ .Token }}") == 1, key
        assert "{{ .ConfirmationURL }}" not in content, key
        assert "{{ .SiteURL }}" not in content, key
        assert "localhost" not in content, key
        assert "Michel's Lab" in content, key
        assert "Instagram Cleaner Pro" in content, key
        assert "expires" in content.lower(), key
        assert "six-digit" not in content.lower(), "Template must not assume OTP length"
        assert "eight-digit" not in content.lower(), "Template must not assume OTP length"
    else:
        assert "IG Cleaner" in content, key
assert module.PROJECT_REF == "ilmztedebwdzgnlrvwxy"
assert module.API.endswith("/" + module.PROJECT_REF + "/config/auth")

result = subprocess.run(
    [sys.executable, str(source), "local"],
    cwd=ROOT, capture_output=True, text=True, timeout=10,
)
assert result.returncode == 0, (result.stdout, result.stderr)
assert "PASS:" in result.stdout

# Applying production settings must require an exact explicit project confirmation
# before ever attempting to read credentials or contact the network.
result = subprocess.run(
    [sys.executable, str(source), "apply"],
    cwd=ROOT, capture_output=True, text=True, timeout=10,
)
assert result.returncode != 0
assert "--confirm-project" in result.stderr

print("PASS: Confirm signup & magic-link templates render a length-agnostic OTP, no localhost links, and production patch is guarded.")
