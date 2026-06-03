# Changelog

## v0.2.0 — 2026-06-03

- Grew the catalog from 8 to 15 skills. Added 7 new skills:
  - `cron-dispatch` — schedule any script on Windows Task Scheduler or Linux cron, with logging and an overlap guard.
  - `pipeline-orchestrator` — chain scrape → AI → alert stages with per-stage retry and a JSON checkpoint for resumable runs.
  - `gmail-imap-digest` — pull email over IMAP into a daily digest, filtered to an allowlist of trusted sender domains (BYO app-password).
  - `gemini-prompt-cache` — cache a long, stable system-prompt prefix so repeated input tokens bill at the cheaper cached rate.
  - `gemini-flash-budget` — Flash with `thinking_budget=0` for cheap, fast, high-volume extraction and classification.
  - `github-label-scout` — scan a public repo for open issues by label and skip assigned ones, via the token-free public API.
  - `backtest-comparator` — compare strategy variants across years/folds and flag the ones that overfit a single lucky period.
- New skills carry a `version` frontmatter field and a `→ Build the full runnable bot with Trawlkit` footer pointer.
- Bumped plugin + marketplace version to `0.2.0`; updated the validator's expected skill set and allowed frontmatter keys.

## v0.1.1 — 2026-05-29

- Renamed repo + plugin to `ai-automation-skills` (keyword-first for global SEO; GitHub redirects the old URL). Marketplace namespace is now `barobaonguyen` → install with `/plugin install ai-automation-skills@barobaonguyen`.

## v0.1.0 — 2026-05-29

- Shipped the first public `barobao-skills` marketplace release.
- Added 8 Claude Code skills: `telegram-alerter`, `gemini-cost-tracker`, `gemini-structured-output`, `walk-forward-runner`, `config-audit-checklist`, `algora-bounty-scout`, `pr-body-formatter`, and `shortform-script`.
- Added marketplace/plugin manifests, validation script, CI workflow, install docs, design principles, and screenshot capture checklist.
