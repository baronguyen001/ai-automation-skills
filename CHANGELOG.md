# Changelog

## v0.3.0 — 2026-06-06

- Grew the catalog from 15 to 20 skills. Added 5 new skills:
  - `webhook-receiver` — a tiny stdlib HTTP server that verifies an HMAC signature in constant time and queues each payload to disk for a worker to drain (no web framework).
  - `sqlite-state` — durable run-state between scheduled runs over one SQLite file: a seen-set for dedup, a key/value cursor to resume, and order-preserving new-item filtering.
  - `proxy-rotator` — rotate a pool of HTTP/SOCKS proxies round-robin with failure tracking and a cooldown that benches dead proxies (BYO list via env; none shipped).
  - `gemini-vision-extract` — structured extraction from an image with Gemini, constrained to a Pydantic `response_schema` so the result is typed JSON, not prose.
  - `playwright-login-session` — capture a `storage_state` once via manual login, then reuse it headless so later runs start already signed in (no committed cookies).
- Fixed the stale `barobaonguyen` GitHub namespace (the account was renamed to `baronguyen001`; GitHub only redirected): manifests, plugin homepage/repository/author, install commands, README badges, and LICENSE now point at `baronguyen001`. The marketplace install is now `/plugin install ai-automation-skills@baronguyen001`. (The `x.com/barobaonguyen` handle is unchanged — it is still the live X account.)
- Bumped plugin + marketplace version to `0.3.0`; updated the validator's expected skill set and version gate.

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
