# IG Cleaner Pro — Project Log & Functional Contract

_Last updated: 2026-09-29_

This file is the **functional contract** for IG Cleaner Pro. UI redesigns, refactors, performance work, and future releases must preserve the capabilities listed here unless Michel Armando Duarte Flores explicitly requests their removal.

## Stable reference

- **Stable functional baseline:** v119 — HTML comparable-range · JSON intact.
- Experimental v120.x redesign previews are **not** allowed to redefine or silently remove v119 functionality.
- Before merging a redesign into `main`, compare the new build against this contract and the v119 baseline.

---

## Non-negotiable architecture

### Review = Following only

Review is exclusively for accounts **Michel follows**.

It must preserve:
- Following cleanup workflow.
- Foco 20 / 30 / 40.
- Recommended batches.
- Recheck / second-review workflow.
- Double Check workflow.
- Protected / reviewed / snoozed states.
- Current-session counters and active-batch tracking.
- Saved history/activity.
- Filters and direct views for accounts that do not follow back.

**Do not reintroduce a "Clean followers" mode inside Review.** Followers has its own dedicated workspace.

### Followers = people who follow the account

Followers must preserve its own dedicated workspace and must not be reduced to a passive table.

It must include:
- Its **own focus controls**.
- Its **own batch/session bar**, equivalent in usefulness to Review.
- Saved history/activity visible inside Followers.
- Search, filters, relation status, risk, review state, protection, and profile actions.
- A Mutuals subview for followers Michel also follows.

### Mutuals

Mutuals is a sub-workflow inside Followers.

It must preserve:
- Foco 20 / 30 / 40.
- Recommended batch.
- Risk batch.
- Review state and protection.
- Its own session/progress tracking.
- Relationship context and review history.

### Pending

Pending is exclusively for pending follow requests.

It must preserve:
- Pending-specific focus/recommended/risk workflows.
- Pending session tracking.
- Pending review/decision state.
- Cross-check logic against Following/Followers.
- No Review or Followers focus may appear here by accident.

---

## Review — mandatory second-review system

The following controls and their behavior are **mandatory** and must not disappear during UI redesign:

### Revisar de nuevo 30
- Reopens accounts that **currently do not follow back**, even if they were already reviewed.
- Must allow already-reviewed rows to be checked again.
- Must show a confirmation popup after opening.
- Must update the review state when confirmed.
- Uses its own cycle/history state so the workflow can rotate through candidates.

### Double Check 30
- Opens accounts that **currently do not follow back**.
- Rotates through different profiles instead of repeatedly serving the same first 30.
- Maintains a separate seen/cycle state.
- Must show a confirmation popup.
- When all current candidates have passed through the cycle, the user can reset/restart the cycle.

### Ver NO ME SIGUE revisados
- Must remain available.
- Shows accounts that currently do not follow back **including already-reviewed accounts**.
- This view exists specifically so previously reviewed relationships can be validated again.

### Cycle controls
Keep visible controls for:
- Reset Double Check cycle.
- Reset Recheck / Revisar de nuevo cycle.

Do not replace these with a generic focus button.

---

## Focus behavior — mandatory

All Focus-style flows must:
- Open Instagram profiles in tabs.
- Leave a confirmation/review UI open in IG Cleaner.
- Preserve active-batch state until the user resolves or cancels it.
- Avoid mixing candidates from another module.
- Never let a global focus control silently switch between Review, Followers, Mutuals, or Pending.

### Context under each username

Where Focus/Recheck/Double Check shows a username, show useful relationship context directly below it when data is available, for example:

- `Lo sigues desde 2022`
- `Te sigue desde 2021`
- `No te sigue`
- `Revisado hace 18 días`
- `Nunca revisado`
- `Te dejó de seguir`

This is context for the user, not a hidden scoring explanation.

---

## Batch/session tracking — mandatory

Review, Followers, Mutuals, and Pending must retain useful batch/session feedback where applicable, including:
- Batches today.
- Reviewed today.
- Reopened/rechecked.
- Active batch.
- Available/openable candidates.
- Last action.
- Ability to recover/reopen/cancel an active batch when supported.

A one-line "Last action" message **does not replace** the batch/session system.

---

## Saved history/activity — mandatory

The app must preserve the automatic review/activity history.

Followers must have a visible saved-history/activity area comparable to Review, scoped to the relevant Followers/Mutuals workflow.

Do not replace the history table/list with only a "last action" label.

History should preserve useful events such as:
- opened
- reopened
- reviewed
- unconfirmed
- snoozed
- last section
- last decision
- last opened
- last reviewed

Export of automatic history must remain available when supported by the stable baseline.

---

## Relationship evidence rules

- Do not treat missing accounts in a partial HTML export as confirmed non-followers.
- JSON behavior from the stable baseline must not be changed casually.
- Relationship conclusions must respect the comparable-range / evidence safeguards already implemented.
- UI redesigns must never weaken evidence correctness.

---

## UX rules

- Primary visual direction is **dark**, not light.
- Avoid generic admin-dashboard styling.
- Redesigns may change layout and visual hierarchy, but **must not remove functionality**.
- Do not duplicate the same workflow in multiple modules.
- Each module owns its actions:
  - Review → Following
  - Followers → Followers
  - Mutuals → mutual followers
  - Pending → pending requests
- Do not add context-dependent global buttons that can trigger the wrong module.
- Keep Focus and review actions obvious and local to their section.

---

## Regression checklist before merge

Before any future build is merged to `main`, verify at minimum:

- [ ] Review still contains Following Focus.
- [ ] Revisar de nuevo 30 is visible and functional.
- [ ] Double Check 30 is visible and functional.
- [ ] Ver NO ME SIGUE revisados is visible and functional.
- [ ] Double Check and Recheck cycle reset controls exist.
- [ ] Followers has its own Focus workflow.
- [ ] Followers has its batch/session bar.
- [ ] Followers has visible saved history/activity.
- [ ] Mutuals has its own Focus workflow.
- [ ] Pending has only Pending actions.
- [ ] No cross-module Focus button appears in the wrong section.
- [ ] Focus cards show relationship-age/review context when available.
- [ ] Active batch can be recovered/resolved.
- [ ] Protected/reviewed/snoozed states are preserved.
- [ ] Relationship evidence safeguards are preserved.
- [ ] JSON import logic remains intact unless intentionally changed and tested.
- [ ] About / Legal / Version remain available.
- [ ] No duplicate DOM IDs.
- [ ] All scripts pass syntax validation.
- [ ] Existing saved local state remains compatible or migration is provided.

---

## 2026-09-29 — redesign lesson

During the v120.x UI experiments, several regressions were found:
- Followers controls were replaced with generic Focus buttons.
- Followers lost its batch/session presentation.
- Followers lost visible saved history.
- The second-review / Recheck / Double Check controls disappeared from the redesigned Review UI.
- A global/contextual Focus control could show actions from the wrong module.

These are now explicitly documented as **regressions that must not recur**.

The redesign may continue, but functionality must be preserved first and reorganized second.


## 2026-09-29 — mandatory module sidebars

The right-side **live sidebar is part of the functional UX contract**, not an optional decoration.

- **Review** keeps its existing right-side live panel.
- **Followers** must have its own right-side live panel with Followers/Mutuals-specific data.
- **Pending** must have its own right-side live panel with Pending-specific data.
- These sidebars should contain the module's live/session information such as last action, opened/reviewed counts, pending/resolved state, active batch, reopen counts, module-specific status, saved history/activity, and relevant quick actions.
- When Followers switches between **All Followers** and **Mutuals**, the same Followers sidebar may update its scope, but it must remain visible.
- Do **not** replace these sidebars with session/history cards inserted into the central workspace.
- The central workspace is for the module's focus controls, filters, tables and primary content; live tracking belongs in the right sidebar.
- A redesign that removes either the Followers or Pending sidebar is a regression.
