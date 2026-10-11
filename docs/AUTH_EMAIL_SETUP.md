# Instagram Cleaner Pro — Fix sign-up verification email and brand sender

**Status 2026-10-11:** The canonical six-digit templates and an opt-in deploy/check utility are committed in the IG Cleaner repository. **This is NOT evidence that hosted Supabase Auth templates, Site URL, Brevo or sender domain have been changed.** The Supabase connector currently available in ChatGPT cannot modify Auth email templates, URL configuration, sender SMTP settings or Brevo sender verification. Publishing another APK will not itself fix the hosted email.

## Diagnosed failure (from actual user screenshots)

- IG Cleaner Desktop and native Android call `POST /auth/v1/otp` with `create_user:true`; UI expects a numeric code and then `POST /auth/v1/verify` with `type:email` before setting a password.
- Hosted mail instead says **Confirm your email address** and supplies a link, consistent with Supabase's default `{{ .ConfirmationURL }}` template for a first-time signup.
- The link redirects to `http://localhost:3000/#error=access_denied&error_code=otp_expired...`, which has no listening IG Cleaner server. It is a default local-development URL inappropriate for the Desktop standalone HTML/Android production app.
- The sender seen in Gmail is `IG Cleaner <realmichelduarte@12366255.brevosend.com>` (Brevo provider subdomain) and Gmail marked it **Spam**. That is **not** a corporate `@michelslab.dev` address. Do not impersonate an unverified domain.
- This is an Auth delivery / template problem, not an Instagram account export/sync migration problem. Existing customer/workspace data must remain untouched.

## Fix now in Supabase dashboard (no app reinstall necessary for mail templates)

Project: **ig-cleaner-sync**, ref `ilmztedebwdzgnlrvwxy`.

1. Open [Authentication → Email Templates](https://supabase.com/dashboard/project/ilmztedebwdzgnlrvwxy/auth/templates).
2. Edit **Confirm sign up**: subject `Your IG Cleaner verification code`; replace the entire email body with the literal HTML from [`supabase/email-templates/confirmation.html`](../supabase/email-templates/confirmation.html). It contains exactly one `{{ .Token }}` and no confirmation link.
3. Edit **Magic Link**: use the same subject and the HTML from [`supabase/email-templates/magic_link.html`](../supabase/email-templates/magic_link.html). This protects OTP login/recovery for existing users too. Save both.
4. Open [Authentication → URL Configuration](https://supabase.com/dashboard/project/ilmztedebwdzgnlrvwxy/auth/url-configuration). **Do not replace localhost with a made-up domain.** If the project uses code-only auth for the standalone/Android apps, links are not used in this flow. For any other link-based auth still enabled, provision an actual owned HTTPS web landing/callback before changing Site URL or allowlist; remove `localhost:3000` as the production fallback only once a valid replacement is available.
5. Open [Authentication → SMTP Settings](https://supabase.com/dashboard/project/ilmztedebwdzgnlrvwxy/auth/smtp). Set a clearly branded **Sender name** such as `Michel's Lab · IG Cleaner Pro`. The **From email** must be a verified sender that the delivery provider actually authorizes; the UI display name alone does not change its mailbox/domain. Do not configure `no-reply@michelslab.dev` unless `michelslab.dev` is registered and its SPF/DKIM/DMARC records are properly verified with Brevo. Otherwise delivery and anti-spoofing checks may fail.
6. In Brevo, confirm the verified sender identity and (if using a custom domain) authenticate DNS SPF/DKIM/DMARC. A personal name under `@brevosend.com` is a sending-provider fallback, not a production branded sender. Gmail `michelslab.dev@gmail.com` is **not** a mailbox on the `michelslab.dev` domain and does not prove that domain is owned or verified.

## Optional idempotent template deployment via Supabase Management API

For maintainers **with an existing management access token stored privately as a local environment variable** (never in source, GitHub comments or chat), the repo includes `tools/configure_auth_email_templates.py`. The tool only updates the four template/subject fields; no SMTP credentials, redirect URLs, databases, users or RLS policies.

```bash
python3 tools/configure_auth_email_templates.py local
# after configuring SUPABASE_ACCESS_TOKEN privately on the maintainer machine:
python3 tools/configure_auth_email_templates.py status
python3 tools/configure_auth_email_templates.py apply --confirm-project ilmztedebwdzgnlrvwxy
python3 tools/configure_auth_email_templates.py status
```

`status` and `apply` use `https://api.supabase.com/v1/projects/ilmztedebwdzgnlrvwxy/config/auth`; success requires **a remote verification**, not merely a local template test. The exact management API fields are: `mailer_subjects_confirmation`, `mailer_templates_confirmation_content`, `mailer_subjects_magic_link`, `mailer_templates_magic_link_content`. The utility requires an exact project ID for writes and never prints tokens. It must not be run with anonymous/publishable API keys.

## Actual end-to-end acceptance (pending until executed)

- [ ] Create a new test login from **Desktop**; receive a **six-digit code** in a new email with branded display name and **not** a link to localhost; verify and set password; sign out and sign in again.
- [ ] Repeat sign-up with a separate test login from **Android**; verify the same code-based process works. An already-used or expired code must be rejected safely and **Send code** should issue a fresh token.
- [ ] Verify password recovery for an existing account and check both `Confirm sign up` and `Magic Link` templates in the hosted project. The confirmation template is particularly important for a brand-new email.
- [ ] Verify mail deliverability (Inbox vs Spam) and sender **actual address**, not only sender display name; check SPF/DKIM/DMARC only for owned, configured domains.
- [ ] Confirm `localhost:3000` no longer appears in any auth email that app users are instructed to use.
- [ ] Confirm two different IG Cleaner logins keep separate Instagram profile registries and saved reviews across Desktop/Android, as tracked in issue #24.

**Key operational constraint:** The repo's production stable remains **v120.41**. This task does **not** authorize a v120.42 APK/HTML release. Fixing hosted email templates takes effect server-side as soon as saved, without changing application version.

References: [Supabase email templates](https://supabase.com/docs/guides/auth/auth-email-templates), [passwordless email](https://supabase.com/docs/guides/auth/auth-email-passwordless), [SMTP configuration](https://supabase.com/docs/guides/auth/auth-smtp).
