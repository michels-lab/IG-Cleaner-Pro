# Instagram Cleaner Pro — Fix sign-up verification email and brand sender

**Status 2026-10-11:** The intended sender is **`michelslab.dev@gmail.com`** (owned Gmail account; no `michelslab.dev` domain). Gmail SMTP is a conditional small-volume solution requiring the user's own Google two-step verification/app password; it has **not** been connected. The canonical six-digit templates and an opt-in deploy/check utility are committed in the IG Cleaner repository. **This is NOT evidence that hosted Supabase Auth templates, Site URL, Brevo or sender domain have been changed.** The Supabase connector currently available in ChatGPT cannot modify Auth email templates, URL configuration, sender SMTP settings or Brevo sender verification. Publishing another APK will not itself fix the hosted email.

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
5. **Confirmed owner choice (2026-10-11):** Michel's Lab currently uses the genuine personal Gmail account **`michelslab.dev@gmail.com`**; the company has **not** purchased or authenticated the domain `michelslab.dev`. Do not use `no-reply@michelslab.dev` or the old personal account `realmichelduarte` in the outgoing sender configuration.
6. **Do not use Brevo to claim Gmail as the From address.** Brevo's published sender policies replace free Gmail sender domains with `@brevosend.com` or a Brevo transactional domain because the user cannot authenticate `gmail.com` in Brevo. This explains why the reported email displayed a fallback domain and could be treated as Spam. Changing the Brevo display name or a sender field does not fix this.
7. **For a small-volume Gmail-sender test**, switch Supabase custom SMTP from Brevo to **Gmail SMTP** *only after* the owner configures two-step verification and generates a dedicated Google **app password** for this connection (not the Google account's normal password). Set:
   - **Sender name:** `Michel's Lab · IG Cleaner Pro`
   - **Sender email:** `michelslab.dev@gmail.com`
   - **SMTP host:** `smtp.gmail.com`
   - **SMTP port:** `465` (SSL/TLS; if configuration requires STARTTLS instead, use `587`).
   - **SMTP username:** `michelslab.dev@gmail.com`
   - **SMTP password:** the *Google app password*, privately entered **directly in the Supabase dashboard**. Never send the password in chat, a screenshot, GitHub issue or repository.
   - **Supabase SMTP page:** [Authentication → SMTP Settings](https://supabase.com/dashboard/project/ilmztedebwdzgnlrvwxy/auth/smtp).
8. **Google account prerequisite:** open [Google Security → 2-Step Verification](https://myaccount.google.com/security) for `michelslab.dev@gmail.com`, turn it on, then access [Google App Passwords](https://myaccount.google.com/apppasswords) and create an app password named `IG Cleaner Supabase SMTP`. The app-password feature is unavailable for some Google account security configurations; do not weaken protection to force it. Google discourages app passwords when an OAuth alternative exists. This is a conditional, low-volume workaround, not proof of production-scale deliverability.
9. Keep Supabase Auth email confirmation **enabled**. Save both OTP templates; request a *new* code from the app and verify the actual delivered email address, code and password sign-in. Google personal Gmail has volume/abuse limitations; revisit an owned authenticated sending domain when the product grows. No one should claim production SMTP has been changed until an actual send-and-verify test succeeds.

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
- [ ] Verify mail deliverability (Inbox vs Spam) and actual sender **`michelslab.dev@gmail.com`**, not just display name; confirm no `brevosend.com` fallback. Do not claim to authenticate `gmail.com` through Brevo.
- [ ] Confirm `localhost:3000` no longer appears in any auth email that app users are instructed to use.
- [ ] Confirm two different IG Cleaner logins keep separate Instagram profile registries and saved reviews across Desktop/Android, as tracked in issue #24.

**Key operational constraint:** The repo's production stable remains **v120.41**. This task does **not** authorize a v120.42 APK/HTML release. Fixing hosted email templates takes effect server-side as soon as saved, without changing application version.

References: [Brevo replacement policy](https://help.brevo.com/hc/en-us/articles/14925263522578-Comply-with-Gmail-Yahoo-and-Microsoft-s-requirements-for-email-senders), [Google app passwords](https://support.google.com/accounts/answer/185833), [Supabase Gmail SMTP reference](https://supabase.com/docs/guides/troubleshooting/using-google-smtp-with-supabase-custom-smtp-ZZzU4Y), [Supabase email templates](https://supabase.com/docs/guides/auth/auth-email-templates), [passwordless email](https://supabase.com/docs/guides/auth/auth-email-passwordless), [SMTP configuration](https://supabase.com/docs/guides/auth/auth-smtp).
