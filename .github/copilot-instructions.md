# Copilot instructions — IG Cleaner Pro

Read `AGENTS.md`, `PROJECT_LOG.md` and the relevant infrastructure/handoff documentation before editing.

Preserve the canonical Desktop engine and established cleanup workflows. Mobile-specific UX is allowed, but required feature parity must not be removed.

Keep raw Instagram exports local. Supabase is for authenticated workflow metadata/state unless a reviewed architecture change explicitly says otherwise. Never commit privileged keys or user export data.

Use current-commit validation for import, state migration, Focus/review/audit behavior, Android builds and sync changes. Device/provider claims remain unvalidated until actually exercised.

Update `PROJECT_LOG.md` for meaningful work. Do not publish a release unless explicitly assigned.

Product identity / About are fundamental product contracts. Treat the approved stacked-layers + sparkle geometry as the visual foundation across IG Cleaner Pro, not as a sticker. About must lead with IG Cleaner Pro identity/version, then About the author with the canonical Michel Duarte portrait, then the official Michel's Lab parent-brand mark, then social links rendered as **network icon + visible network name** using canonical profile URLs.



For logo/About/branding work, follow the Michel-Software-Standards Product Identity Standard and BRAND_ADOPTION_PLAYBOOK. Replace actual platform identity references, adapt the official geometry to this app's existing visual language, avoid sticker-style logo placement, preserve unrelated behavior, validate the build, and do not release without explicit authorization.


For logo/About/branding work, follow the Michel-Software-Standards Product Identity Standard and BRAND_ADOPTION_PLAYBOOK. Replace actual platform identity references, adapt the official geometry to this app's existing visual language, avoid sticker-style logo placement, preserve unrelated behavior, validate the build, and do not release without explicit authorization.

## Structured handoff requirement

For any tracked Michel's Lab task, return enough machine-readable continuation context for the master handoff registry:

- task ID and repository;
- owner/role and branch;
- outcome;
- commits and areas changed;
- validations that **actually ran** and their real result;
- evidence status: `verified`, `inferred`, or `blocked`;
- remaining work;
- blockers/manual evidence still required;
- suggested next owner/role when useful.

Do not list planned tests/builds/device checks as completed validation. If required validation was not performed, the task must be released/handed back with that work pending rather than described as complete.


