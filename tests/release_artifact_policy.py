"""Resolve version-bearing release assets without mistaking the next reservation for a published binary.

Called by source contracts on a requested FINAL release and the published
receipt after authorization was consumed. Does not publish or modify assets.
"""
import re


def artifact_release_tag(manifest, request):
    policy = manifest["releasePolicy"]
    current = policy["currentStableRelease"]
    reserved = policy["nextRelease"]
    if not all(re.fullmatch(r"v[0-9]+\.[0-9]+", tag) for tag in (current, reserved)):
        raise ValueError("Invalid current/reserved release tags")
    if current == reserved:
        raise ValueError("Next release must differ from the published stable")

    state = request.get("status")
    authorized = request.get("authorized")
    if authorized is True and state in ("requested", "authorized"):
        artifact_tag = reserved
    elif authorized is False and state == "published":
        artifact_tag = current
        if (request.get("published_run") != policy.get("lastPublishedRun")
                or request.get("published_commit") != policy.get("lastPublishedCommit")
                or request.get("published_at") != policy.get("lastPublishedAt")
                or request.get("published_release_url") != policy.get("lastPublishedReleaseUrl")):
            raise ValueError("Published request and manifest provenance disagree")
    else:
        raise ValueError("Release request must be explicitly authorized or published/consumed")

    if request.get("tag") != artifact_tag or request.get("version") != artifact_tag[1:]:
        raise ValueError("Release request identity does not match its artifact version")
    return artifact_tag
