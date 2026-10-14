INSTA CLEANER PRO — WINDOWS APPLICATION
Michel's Lab | TOOLS WITH IDENTITY.

This package contains the integrated Windows application. Use InstaCleanerPro.exe.
No separate HTML, .cmd launcher or Python installation is required for normal use.
Check BUILD-INFO.txt for the exact source commit and distribution identity. GitHub
Releases is the official download channel. A ZIP from GitHub Actions or a PR is
development evidence, not an official release.

GETTING STARTED
1. Extract the complete ZIP to a folder you control.
2. Double-click InstaCleanerPro.exe. It opens Insta Cleaner in its own Chrome
   application window and starts the private local robot controller internally.
3. Sign in to your IG Cleaner account if using optional cross-device sync, then
   select the correct Instagram workspace. IG Cleaner login and Instagram login
   are different identities.
4. To collect visible counts, open Insights > Profile Counts and explicitly start
   a collection. When a separate Chrome window appears, sign in to Instagram
   directly at instagram.com. The application never asks you to type your
   Instagram password into an IG Cleaner form.
5. To perform account-changing actions, open Automations. Choose Cancel Sent
   Requests or Unfollow Non-Followbacks, review the exact queue, exclusions and
   pacing, then approve the batch. No account-changing job starts merely by
   launching Insta Cleaner.
6. Mutuals is human-review-only: Focus 20/30/40 does not automate unfollowing.
   Followback Audit is optional, read-only, and never a prerequisite for Unfollow.

SAFETY AND EVIDENCE
- Automated browser tests use simulated Instagram pages. They do NOT prove
  correct behavior in a live owner's Instagram session. Begin with a small,
  supervised batch only after checking the exact target profiles.
- A protected/skipped account must not be acted on. The robot verifies signed-in
  owner, exact target, visible button state and outcome, and stops on ambiguity,
  account mismatch, login/challenge or platform restrictions. Do not bypass
  challenges or reattempt ambiguous account-changing clicks.
- Import complete Following and Followers exports before non-followback
  automation. Partial exports do not establish a negative followback.
- Pausing preserves progress. Successful actions are not repeated on resume.
  Statuses can require manual verification; a browser click alone is not proof.
- Instagram can change its website or restrict automated collection and actions.
  No collection speed or uninterrupted execution is guaranteed.

DATA AND UPDATES
- The integrated application's browser profile is persistent under
  %LOCALAPPDATA%\Michels Lab\Insta Cleaner Pro\
- The local robot's browser cookies and journals live under
  %USERPROFILE%\.ig-cleaner-pro\
- Browser cookies and session files are private. Never upload or share them.
- An earlier standalone HTML file may use a different storage origin. It is
  NOT automatically migrated into the Windows application's profile. Export a
  full backup from Vault and import it in the new app before retiring the old
  file. Keep the old copy until lists, reviews, protections and Focus history
  have been verified.
- Original Instagram export ZIP/JSON/HTML input stays on your device. Optional
  authenticated sync sends supported normalized app state to Supabase, not the
  original ZIP. Cloud deletion and local backups are distinct operations.
- Windows and Android do not run the same robot: Windows collection does not
  automatically transfer newly collected third-party counts to Android.
- This EXE is not a Microsoft Store-signed installation. Do not disable
  antivirus, SmartScreen or Windows security controls to run an untrusted file.

TECHNICAL VALIDATION
CI tests the frozen EXE using InstaCleanerPro.exe --healthcheck, an offline Chromium mock Instagram
flow, and Desktop/Android contracts. These checks are NOT a live user-session
acceptance test. Keep BUILD-INFO.txt and EXECUTABLE-SHA256.txt with the EXE;
they identify the candidate and its hash.
