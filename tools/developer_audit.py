#!/usr/bin/env python3
"""Read-only, privacy-redacted developer diagnostic report for IG Cleaner Pro.

This module never opens Instagram, copies sessions, or changes a relationship.
Only aggregate counts, source-owned status names and fixed diagnostic codes
leave the owner's local action journal. Handles, cookies, paths and tokens do not.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import re

ACTION_STATES = {"ok", "already_not_following", "already_not_requested", "review", "error", "blocked"}
CLICK_PHASES = {"relationship_control", "unfollow_menu",
                "private_unfollow_confirmation", "cancel_request_confirmation"}
SAFE_ISSUES = {"missing_profile_info", "profile_load_timeout"}
ISSUE_CODES = {
    "missing_profile_info", "profile_load_timeout", "requires_manual_review",
    "unexpected_followback", "pending_cancel_unverified",
    "pending_already_following", "pending_not_requested", "mutual_before_action",
    "interrupted_action_uncertain"
}
MAX_BYTES = 5_000_000
SAFE_REVISION = re.compile(r"(?:unknown|v?[0-9]+\.[0-9]+|[0-9a-fA-F]{7,40})\Z")
SAFE_LIMITATIONS = (
    "Offline journal analysis cannot confirm a real Instagram relationship change.",
    "A possibly completed click must never be retried from this audit.",
    "Source/UI checks do not substitute for installed Windows and live-owner testing.",
)


def _safe_revision(value):
    return value if isinstance(value, str) and SAFE_REVISION.fullmatch(value) else "unknown"


def _safe_number(value):
    return value if type(value) is int and 0 <= value <= 1_000_000_000 else 0


def _safe_counts(values, allowed):
    if not isinstance(values, dict):
        return {}
    keys = sorted(key for key in values if isinstance(key, str) and key in allowed)
    return {key: values[key] for key in keys
            if type(values[key]) is int and 0 <= values[key] <= 1_000_000_000}


def _safe_generated_at(value):
    if not isinstance(value, str) or len(value) > 50:
        return "unknown"
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return "unknown"
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return "unknown"
    return parsed.astimezone(timezone.utc).isoformat()


FINDING_CATALOG = {
    "JOURNAL_TOO_LARGE": ("warning", "Oversized action journal; inspect disk storage locally."),
    "JOURNAL_UNREADABLE": ("error", "Action journal could not be parsed; preserve before repair."),
    "INVALID_ACTION_RECORD": ("error", "Non-object journal entry; preserve provenance."),
    "RETRYABLE_ZERO_CLICK": ("warning", "Proven pre-click failures may be rechecked automatically in the authorized cohort."),
    "UNCERTAIN_OR_MANUAL": ("warning", "Unverified outcome: read-only evidence required; never repeat a possible click."),
    "INTERRUPTED_ACTION_INTENT": ("error", "Durable intent was written before an Instagram relationship click but the outcome was not saved. Inspect exact target read-only; NEVER replay automatically."),
    "NONFOLLOW_EVIDENCE_INCONSISTENT": ("error", "Terminal already-not-following lacks expected evidence marker."),
    "BATCH_AWAITING_OWNER_APPROVAL": ("info", "Unapproved batch retained; automatic results are not Reviewed."),
    "MULTIPLE_UNAPPROVED_COHORTS": ("warning", "Several unapproved cohorts; reconcile scope without deleting history."),
    "BATCH_REVIEW_UNREADABLE": ("error", "Batch review document could not be parsed."),
    "HISTORICAL_READONLY_NOT_FOLLOWING": ("info", "Historical recheck observed absence of outgoing follow; no Unfollow clicked and not marked Reviewed."),
    "HISTORICAL_READONLY_UNRESOLVED": ("warning", "Historical profile still lacks reliable read-only verification; original action result remains untouched."),
    "HISTORICAL_READONLY_REPORT_UNREADABLE": ("warning", "Historical read-only ledger could not be read; original journal preserved."),
    "AUDIT_ROOT_IS_SYMLINK": ("error", "Developer audit root is a link; select its real, private workspace directory."),
    "EXTERNAL_JOURNAL_LINK_SKIPPED": ("warning", "Linked action-journal file was skipped to keep the Developer audit inside its local workspace."),
}


def _safe_status(value):
    return value if isinstance(value, str) and value in ACTION_STATES else "other"


def run_audit(data_root: Path, *, source_revision: str = "unknown") -> dict:
    """Read aggregate journaling evidence without exposing profile identifiers.

    Never glob outside data_root; file basenames are not included in findings.
    A broken/oversized journal creates a diagnostic code, not a raw exception.
    """
    result = {
        "schema": "michels-lab-developer-audit-v1",
        "product": "IG Cleaner Pro",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_revision": _safe_revision(source_revision),
        "mode": "developer-read-only",
        "privacy": "aggregates-only-no-usernames-no-cookies-no-tokens",
        "journals": 0, "profiles": 0, "unapproved_batches": 0,
        "historical_readonly_observations": 0,
        "action_status_counts": {}, "issue_code_counts": {},
        "interrupted_action_intents": 0, "click_phase_counts": {},
        "findings": [], "limitations": list(SAFE_LIMITATIONS),
    }
    root = Path(data_root)
    # An attacker-controlled link to an outside folder must never turn the
    # local, aggregate-only Developer audit into a reader of unrelated files.
    if root.is_symlink():
        result["findings"].append({
            "code": "AUDIT_ROOT_IS_SYMLINK", "severity": "error", "count": 1,
            "action": FINDING_CATALOG["AUDIT_ROOT_IS_SYMLINK"][1]
        })
        return result
    if not root.exists():
        result["findings"].append({"code": "JOURNAL_DIRECTORY_MISSING", "severity": "info",
                                   "count": 1, "action": "Run the installed app before inspecting saved history."})
        return result
    status_counts, issue_counts, finding_counts, phase_counts = (
        Counter(), Counter(), Counter(), Counter())
    for path in sorted(root.glob("instagram-actions-*.json")):
        # Skip derived/auxiliary history; count it via the dedicated loop below.
        if path.name.endswith(("-batch-reviews.json", "-historical-rechecks.json")):
            continue
        if path.is_symlink():
            finding_counts["EXTERNAL_JOURNAL_LINK_SKIPPED"] += 1
            continue
        if not path.is_file():
            continue
        result["journals"] += 1
        try:
            if path.stat().st_size > MAX_BYTES:
                finding_counts["JOURNAL_TOO_LARGE"] += 1
                continue
            data = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                raise ValueError("unexpected-journal-shape")
        except (OSError, ValueError, UnicodeError):
            finding_counts["JOURNAL_UNREADABLE"] += 1
            continue
        for record in data.values():
            result["profiles"] += 1
            if not isinstance(record, dict):
                finding_counts["INVALID_ACTION_RECORD"] += 1
                continue
            status = _safe_status(record.get("status"))
            status_counts[status] += 1
            intent = record.get("click_intent")
            if isinstance(intent, dict) and intent.get("outcome_recorded") is not True:
                finding_counts["INTERRUPTED_ACTION_INTENT"] += 1
                result["interrupted_action_intents"] += 1
                phase = intent.get("phase")
                phase_counts[phase if isinstance(phase, str) and
                             phase in CLICK_PHASES else "other"] += 1
            issue = record.get("issue")
            if issue:
                issue_counts[issue if isinstance(issue, str) and issue in ISSUE_CODES else "other"] += 1
            if status in {"review", "error", "blocked"}:
                msg = str(record.get("message") or "")
                safe_preclick = (
                    msg.startswith("The active Instagram account cannot be verified. No action was performed.")
                    or msg == "Instagram session verification failed before the first click. No action performed."
                    or msg == "Instagram session could not be verified before skipping a non-followed profile."
                    or (isinstance(issue, str) and issue in SAFE_ISSUES and "No action clicked." in msg)
                )
                finding_counts["RETRYABLE_ZERO_CLICK" if safe_preclick else "UNCERTAIN_OR_MANUAL"] += 1
            if status == "already_not_following" and not str(record.get("message", "")).startswith("Already not following:"):
                finding_counts["NONFOLLOW_EVIDENCE_INCONSISTENT"] += 1
    for path in root.glob("instagram-actions-*-batch-reviews.json"):
        if path.is_symlink():
            finding_counts["EXTERNAL_JOURNAL_LINK_SKIPPED"] += 1
            continue
        if not path.is_file():
            continue
        try:
            if path.stat().st_size > MAX_BYTES:
                raise ValueError("oversized")
            batches = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(batches, list):
                raise ValueError("unexpected-batch-shape")
            for entry in batches:
                if isinstance(entry, dict) and not entry.get("approved_at"):
                    result["unapproved_batches"] += 1
                    cohort = entry.get("targets", [])
                    results = entry.get("recheck_results", {})
                    if isinstance(cohort, list) and isinstance(results, dict):
                        finding_counts["BATCH_AWAITING_OWNER_APPROVAL"] += 1
        except (OSError, ValueError, UnicodeError):
            finding_counts["BATCH_REVIEW_UNREADABLE"] += 1
    for path in root.glob("instagram-actions-*-historical-rechecks.json"):
        if path.is_symlink():
            finding_counts["EXTERNAL_JOURNAL_LINK_SKIPPED"] += 1
            continue
        if not path.is_file():
            continue
        try:
            if path.stat().st_size > MAX_BYTES:
                finding_counts["HISTORICAL_READONLY_REPORT_UNREADABLE"] += 1
                continue
            saved = json.loads(path.read_text(encoding="utf-8"))
            rows = saved.get("results", {}) if isinstance(saved, dict) else {}
            if not isinstance(rows, dict): raise ValueError("invalid")
            for row in rows.values():
                if not isinstance(row, dict): continue
                result["historical_readonly_observations"] += 1
                category = row.get("observation")
                if category == "observed_not_following":
                    finding_counts["HISTORICAL_READONLY_NOT_FOLLOWING"] += 1
                elif category == "still_unresolved":
                    finding_counts["HISTORICAL_READONLY_UNRESOLVED"] += 1
        except (OSError, ValueError, UnicodeError):
            finding_counts["HISTORICAL_READONLY_REPORT_UNREADABLE"] += 1
    if result["unapproved_batches"] > 1:
        finding_counts["MULTIPLE_UNAPPROVED_COHORTS"] += 1
    result["action_status_counts"] = dict(sorted(status_counts.items()))
    result["issue_code_counts"] = dict(sorted(issue_counts.items()))
    result["click_phase_counts"] = dict(sorted(phase_counts.items()))
    for code, count in sorted(finding_counts.items()):
        severity, action = FINDING_CATALOG[code]
        result["findings"].append({"code": code, "severity": severity,
                                   "count": count, "action": action})
    return result


def ai_prompt(report: dict, client_checks: dict | None = None) -> str:
    """Stable export: diagnostic categories only, no user-generated values."""
    checks = client_checks if isinstance(client_checks, dict) else {}
    allowed_checks = {
        "duplicate_dom_ids", "missing_critical_controls", "uncaught_ui_errors",
        "unhandled_ui_rejections", "app_revision", "viewport_width"
    }
    safe_checks = {}
    for key in allowed_checks:
        value = checks.get(key)
        if key == "app_revision":
            if isinstance(value, str) and _safe_revision(value) != "unknown":
                safe_checks[key] = value
        elif isinstance(value, int) and not isinstance(value, bool) and 0 <= value <= 1_000_000:
            safe_checks[key] = value
    # The function is also callable outside the session-token loopback server.
    # Never trust free-text or arbitrary fields in a supplied report for an
    # exported AI repair prompt. Only canonical diagnostic codes/descriptions
    # and bounded numeric aggregates may cross the export boundary.
    report = report if isinstance(report, dict) else {}
    findings = []
    raw_findings = report.get("findings")
    for entry in (raw_findings if isinstance(raw_findings, list) else [])[:64]:
        if not isinstance(entry, dict):
            continue
        code = entry.get("code")
        if not isinstance(code, str) or code not in FINDING_CATALOG:
            continue
        severity, action = FINDING_CATALOG[code]
        findings.append({"code": code, "severity": severity,
                         "count": _safe_number(entry.get("count")),
                         "action": action})
    sanitized = {
        "schema": "michels-lab-developer-audit-v1",
        "product": "IG Cleaner Pro",
        "generated_at": _safe_generated_at(report.get("generated_at")),
        "source_revision": _safe_revision(report.get("source_revision")),
        "mode": "developer-read-only",
        "privacy": "aggregates-only-no-usernames-no-cookies-no-tokens",
        "journals": _safe_number(report.get("journals")),
        "profiles": _safe_number(report.get("profiles")),
        "unapproved_batches": _safe_number(report.get("unapproved_batches")),
        "historical_readonly_observations": _safe_number(report.get("historical_readonly_observations")),
        "action_status_counts": _safe_counts(report.get("action_status_counts"), ACTION_STATES | {"other"}),
        "issue_code_counts": _safe_counts(report.get("issue_code_counts"), ISSUE_CODES | {"other"}),
        "interrupted_action_intents": _safe_number(report.get("interrupted_action_intents")),
        "click_phase_counts": _safe_counts(report.get("click_phase_counts"), CLICK_PHASES | {"other"}),
        "findings": findings,
        "limitations": list(SAFE_LIMITATIONS),
    }
    return (
        "You are auditing IG Cleaner Pro Developer Edition. Work from the following "
        "redacted, local-only diagnostics. Identify root causes, prioritize P0/P1/P2, "
        "propose minimal fixes and specific regression tests. Never infer an "
        "Instagram Unfollow from a button click alone; do not replay uncertain clicks. "
        "Preserve journal and account scoping. Distinguish proven zero-click failures "
        "from potentially applied actions. Do not request credentials, session tokens, "
        "Instagram usernames or raw exports.\n\n"
        + json.dumps({"backend": sanitized, "client_ui_checks": safe_checks},
                     ensure_ascii=False, indent=2)
    )
