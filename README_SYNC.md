# IG Cleaner Pro — Desktop + Android + Supabase Sync

Current Android work line: **v120.29 beta**.

## Product model

IG Cleaner is one product with two interaction surfaces:

- **Desktop:** the full single-file IG Cleaner workspace.
- **Android:** the full Desktop workspace packaged inside the app **plus** native mobile Focus, Audit and Account surfaces.

The Android app is not intended to be a reduced companion anymore. The Workspace tab exposes the same Desktop engine/modules; native screens only replace workflows where mobile interaction should differ.

## Shared sync semantics

Supabase stores synchronized **metadata/state**, not the raw Instagram export:

- device identity / last-seen;
- frozen Focus batches and batch items;
- audit events;
- projected per-profile review state.

Rules:
- opening a profile and reviewing a profile are separate events;
- review history is append-only through audit events;
- current review projection uses the newest review timestamp;
- every event preserves source device (`desktop` / `android`);
- Audit never rewrites the original review time;
- Focus prepared on Desktop keeps its exact frozen username order when consumed on Android;
- Android reviews must appear on Desktop after sync, and vice versa.

## Authentication

End users see only:

1. email;
2. **Enviar código**;
3. OTP from email;
4. **Entrar**.

The Supabase Project URL and publishable key are application configuration. They are not user-facing fields.

Never ship a service-role key, database password, SMTP credential, refresh token or other privileged secret.

## Privacy boundary

Instagram ZIP/JSON/HTML import is still processed locally in the client workflow. The current sync architecture is for review/workflow metadata.

Raw Instagram export backup/upload is **not** part of the current sync contract.

## Android v120.29

Android includes:
- Workspace — packaged Desktop engine;
- Focus — one-profile-at-a-time checklist;
- Audit — cross-device review/open history;
- Cuenta — OTP login and sync status.

Workspace integration also provides:
- Android file chooser for HTML/JSON/ZIP import inputs;
- external Instagram-link handling;
- mobile prevention/redirection of Desktop bulk-profile opening;
- bridge for generated exports to Android Downloads;
- session/device bootstrap into the embedded Desktop engine.

## Current validation

GitHub Actions run `37388962937` compiled `android-full-workspace-v120.29` successfully.

Before v120.29 is released, the target-phone validation gate is:
- cold launch;
- full Workspace module rendering;
- ZIP/file picker import;
- OTP/session persistence;
- Desktop ↔ Android Focus round-trip;
- Android review projection back to Desktop;
- Audit origin correctness;
- HTML export to Downloads.

See `PROJECT_LOG.md` for the chronological implementation record.
