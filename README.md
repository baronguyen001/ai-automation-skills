# barobao-skills

8 production-tested Claude skills for automation, Gemini cost control, OSS bounty hunting, and ML strategy validation. Distilled from 8 months of indie-hacker work.

```text
/plugin marketplace add barobaonguyen/barobao-skills
/plugin install barobao-skills@barobao
```

![Skills](https://img.shields.io/badge/skills-8-blue) ![License](https://img.shields.io/badge/license-MIT-green) ![Last commit](https://img.shields.io/github/last-commit/barobaonguyen/barobao-skills) ![Stars](https://img.shields.io/github/stars/barobaonguyen/barobao-skills)

Demo captures are intentionally not fabricated. The needed screenshots are tracked in [screenshots/README.md](screenshots/README.md).

## Install

Run these inside Claude Code:

```text
/plugin marketplace add barobaonguyen/barobao-skills
/plugin install barobao-skills@barobao
```

Then confirm:

```text
/plugin list
```

Installed skills appear under the `barobao-skills:<skill>` namespace.

## What's In The Box

### Automation

| Skill | What it does | Trigger |
|---|---|---|
| `telegram-alerter` | Sends Telegram alerts from Python with env-only credentials, HTML formatting, inline buttons, photo support, and 429 retry handling. | "send a telegram alert", "notify telegram" |

### Gemini Meta

| Skill | What it does | Trigger |
|---|---|---|
| `gemini-cost-tracker` | Logs Gemini token usage and estimated USD cost per call, model, and session. | "track gemini cost", "gemini token usage" |
| `gemini-structured-output` | Gets validated JSON from Gemini with Pydantic response schemas and a JSON salvage parser. | "gemini structured output", "responseSchema" |

### Bounty/Scraping

| Skill | What it does | Trigger |
|---|---|---|
| `algora-bounty-scout` | Scouts public Algora org boards, parses bounty links, dedupes, and filters time-wasters before coding. | "scout algora", "find OSS bounties" |
| `pr-body-formatter` | Builds a complete GitHub PR body from a diff summary and issue reference without TODO placeholders. | "write a PR description", "pr body template" |

### Validation

| Skill | What it does | Trigger |
|---|---|---|
| `walk-forward-runner` | Sets up leakage-free rolling time-series validation and flags overfit parameter rankings. | "walk forward validation", "time series cross validation" |
| `config-audit-checklist` | Audits config drift between a snapshot doc, `.env`, and README defaults before a backtest or deploy. | "config audit", "params drift" |

### Content

| Skill | What it does | Trigger |
|---|---|---|
| `shortform-script` | Drafts short-form or long-form video scripts from a topic plus a creator persona file, using fact slots to avoid invented personal claims. | "write a video script", "tiktok script" |

## Why These 8

Every skill maps to a real pattern used repeatedly across automation, Gemini, validation, and open-source contribution workflows. The point is not a huge catalog; it is a compact set of skills with concrete examples, reusable assets, and enough install structure to work as a Claude Code plugin marketplace.

## 30-Second Example

Trigger:

```text
Track Gemini cost for this batch ranking script.
```

Claude can wrap calls with `gemini-cost-tracker`:

```python
tracker.record("gemini-2.5-flash", resp.usage_metadata)
print(tracker.summary())
```

Example output:

```text
Calls: 3 | Total: $0.001242
  gemini-2.5-flash-lite: $0.000180
  gemini-2.5-flash: $0.001062
```

## Design

See [docs/design_principles.md](docs/design_principles.md). The short version: one concrete example per skill, no `<your value here>` placeholders, no private production parameters, and no secrets.

## Contributing

See [docs/contributing.md](docs/contributing.md) for the frontmatter rules, validation command, and local `claude plugin validate .` check.

## License

MIT. See [LICENSE](LICENSE).

## Star History

Add the Star History chart after the repo has enough public signal to make the chart useful. Until then, this section stays as a placeholder.
