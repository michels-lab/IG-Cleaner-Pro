# IG Cleaner Pro

Local-first workspace for reviewing Instagram exports, comparing following/followers relationships, prioritizing cleanup batches, and preserving review history without logging in to Instagram.

## Current version

**v120.30 beta — Desktop/Android full-list sync**

## What it does

- Loads Instagram following/followers exports in supported JSON or HTML formats.
- Compares relationship data and keeps ambiguous HTML evidence separate from confirmed relationship evidence.
- Provides focus batches, re-check workflows, filters, review history, protected accounts, pending-request analysis, diagnostics, and exports.
- Does not log in to Instagram or automate unfollows. When cross-device sync is enabled, the original Instagram export file remains local, while normalized Following/Followers/Pending profile-list records plus workflow metadata are stored in the user's private Supabase rows.
- Includes an in-app About / Developer, Legal, and Version section.

## Run locally

Download `index.html` and open it in a modern desktop browser. No build step is required.

## Privacy

IG Cleaner Pro analyzes the Instagram export locally and does not use the Instagram API or automate account actions. With cross-device sync enabled, the original ZIP/JSON/HTML file is not uploaded as a backup; normalized profile-list records and review/workflow state are synchronized through the configured Supabase backend under Row Level Security.

## Development contract

Before redesigning or refactoring IG Cleaner Pro, read [PROJECT_LOG.md](PROJECT_LOG.md). It documents the workflows that must not be removed, including Followers session/history, Recheck, Double Check, Focus behavior, and regression checks required before merging to `main`.

## Author

**Michel Armando Duarte Flores**  
Michel's Lab  
GitHub: [@realmichelduarte](https://github.com/realmichelduarte)

## License

This repository is **source-available, not open source**. All rights are reserved. See `LICENSE.txt`.

## Disclaimer

IG Cleaner Pro is an independent tool and is not affiliated with, endorsed by, or sponsored by Instagram or Meta Platforms, Inc.
