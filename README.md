# IG Cleaner Pro

Local-first workspace for reviewing Instagram exports, comparing following/followers relationships, prioritizing cleanup batches, and preserving review history without logging in to Instagram.

## Current version

**v120.20 — ZIP primary import · JSON/HTML parity**

## What it does

- Loads Instagram following/followers exports in supported JSON or HTML formats.
- Compares relationship data and keeps ambiguous HTML evidence separate from confirmed relationship evidence.
- Provides focus batches, re-check workflows, filters, review history, protected accounts, pending-request analysis, diagnostics, and exports.
- Works locally in the browser: no backend, no Instagram login, no automatic unfollow, and no upload of your Instagram export data to a server.
- Includes an in-app About / Developer, Legal, and Version section.

## Run locally

Download `index.html` and open it in a modern desktop browser. No build step is required.

## Privacy

IG Cleaner Pro is designed as a local tool. The app analyzes files you select in your browser. It does not use the Instagram API and does not automate account actions.

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
