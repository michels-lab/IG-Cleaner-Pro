# IG Cleaner Pro — Agent Contract

IG Cleaner Pro is a local-first Instagram export analysis workspace with Desktop/local-Web and Android surfaces plus authenticated Supabase workflow-metadata sync. Before editing, read `.michelslab/project.yml`, `MICHELS_LAB_PROJECT.md`, `PROJECT_LOG.md`, `docs/CURRENT_HANDOFF.md` when present, `docs/INFRASTRUCTURE_AUDIT.md`, and the workflows/tests that own the affected behavior.

Shared Michel's Lab rules live in `realmichelduarte/Michel-Software-Standards`.

## Product constraints

- Preserve the canonical Desktop engine/workspace and established cleanup workflows unless the task explicitly changes them.
- Android may use mobile-specific UX, but it must not silently become a reduced product where parity is required.
- Raw Instagram ZIP/JSON/HTML exports remain local. Current Supabase sync is for authenticated workflow metadata/state, not raw export upload.
- Opened, reviewed, follow-state evidence and device provenance are distinct concepts; do not collapse them.
- Focus batches, Recheck, Double Check, Followers session/history, pending requests, filters and audit/history behavior must not disappear as collateral damage.
- Do not automate Instagram account actions or add Instagram-login dependencies unless explicitly requested and reviewed.
- Preserve the accepted Michel's Lab/IG Cleaner visual family unless redesign is explicitly in scope.
- Never commit Supabase privileged keys, database passwords, SMTP credentials, OTP secrets or user export data.

## About identity — mandatory

About is a primary IG Cleaner Pro brand surface, not a plain metadata/settings page.

It MUST intentionally combine:
- the approved product mark/lockup with prominent visual presence;
- the current canonical Michel Duarte portrait;
- Michel's Lab / developer identity;
- social links using **both the recognizable network icon and the visible network name**.

For social links, render icon + label together (for example Instagram icon + `Instagram`, GitHub icon + `GitHub`). Do not use text-only rows as the finished design, and do not use icon-only controls without a visible/accessibility label.

Use the canonical URLs from the master `brand/developer-profile.json`. Treat the portrait, logo, social controls and metadata as one coherent branded composition derived from the product's visual language.


## Validation

Inspect current CI/workflows and run the strongest relevant current-commit checks. Desktop/local-Web changes must validate import/state migration and the affected interaction flow. Android changes must build the real app path and keep device-only parity/sync/export behavior explicitly open until actually tested.

Supabase changes require RLS/data-boundary reasoning and, when possible, real-provider isolation/round-trip evidence.

## Completion

Update `PROJECT_LOG.md` with meaningful fixes, regressions, decisions and validation. Infrastructure changes also update `docs/INFRASTRUCTURE_AUDIT.md` when relevant.

Do not bump versions or publish releases unless explicitly assigned.
