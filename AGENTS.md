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


## Fundamental visual identity and About — mandatory

This is a **core IG Cleaner Pro product contract**, not optional branding polish.

### Product-wide visual system

The approved stacked-layers + sparkle logo geometry is the foundation of the app's visual system. Preserve the defining silhouette, proportions and spatial relationships. Color, monochrome/inverted treatment, glow, glass, outline, translucency, material and motion may adapt to theme/context.

Do not satisfy branding by pasting the source SVG into unrelated screens. Translate the mark's visual DNA into cards, batches, focus/review hierarchy, selected/completed states, audit/review emphasis, separators, highlights and motion where appropriate. Cleanup workflow clarity, local-first privacy and state semantics remain hard constraints.

### About hierarchy

About MUST be intentionally designed in this order:

1. **Product identity first** — approved IG Cleaner Pro mark/lockup, product name, real current version and product-facing composition derived from the app identity.
2. **About the author** — current canonical Michel Duarte portrait, **Michel Duarte**, and appropriate developer copy.
3. **Michel's Lab parent brand** — official Michel's Lab mark/lockup shown as the studio/ecosystem identity without overpowering IG Cleaner Pro.
4. **Social profiles** — each visible network link shows the recognizable network icon **and** the visible network name together, using canonical URLs from the master `brand/developer-profile.json`.

Do not finish About with text-only social links or icon-only social buttons. Accessibility labels/tooltips supplement the visible network name; they do not replace it.

Treat this hierarchy and the product-wide logo-derived design language as part of product completeness. Visual work must not regress it.

Follow `standards/PRODUCT_IDENTITY_STANDARD.md` and `standards/ABOUT_STANDARD.md` in `realmichelduarte/Michel-Software-Standards`.

## Validation

Inspect current CI/workflows and run the strongest relevant current-commit checks. Desktop/local-Web changes must validate import/state migration and the affected interaction flow. Android changes must build the real app path and keep device-only parity/sync/export behavior explicitly open until actually tested.

Supabase changes require RLS/data-boundary reasoning and, when possible, real-provider isolation/round-trip evidence.

## Completion

Update `PROJECT_LOG.md` with meaningful fixes, regressions, decisions and validation. Infrastructure changes also update `docs/INFRASTRUCTURE_AUDIT.md` when relevant.

Do not bump versions or publish releases unless explicitly assigned.


## Intelligent brand adoption

When the user asks to update/adopt the app logo, icon, splash, startup or About:

- use the canonical product assets from `realmichelduarte/Michel-Software-Standards/shared-assets/product-logos/`;
- follow `standards/PRODUCT_IDENTITY_STANDARD.md` and `standards/BRAND_ADOPTION_PLAYBOOK.md` from the Michel-Software-Standards repository;
- inspect this app's current design system before placing assets;
- replace the real active platform identity references instead of layering the new logo over legacy/generic branding;
- use the app icon for launcher/executable/favicon derivatives, the mark for compact identity, and the lockup for larger splash/About surfaces when appropriate;
- treat the logo geometry as design language where useful, but do not repeat the literal logo across screens;
- build About in the hierarchy Product → Author → Michel's Lab → Social;
- use the canonical Michel Duarte portrait and Michel's Lab mark in About;
- preserve unrelated product behavior;
- update this repository's project/audit log and validate current build/CI;
- do not publish a release unless the user explicitly authorizes it.

A change that merely pastes the SVG/PNG into an arbitrary card or header is not a completed branding migration.

## Cross-chat claim guard

Michel's Lab uses the master `.michelslab/task-claims.json` / generated queue metadata to prevent multiple chats or agents from editing the same tracked task concurrently.

Before starting a delegated tracked task:
- inspect the claim metadata included in the handoff/current master queue when available;
- if a different owner has an active non-stale claim, **stop and report the collision instead of editing**;
- stale claims require a freshness check before work resumes;
- do not treat a claim as validation or release permission;
- return branch/commit/validation status in the handoff so the master owner can heartbeat, complete or release the claim.


