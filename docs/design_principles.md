# Design Principles

## Concrete Beats Generic

Every skill needs one realistic `## Concrete example`. The example should show the input and the exact code or output Claude should produce.

## Installable Beats Markdown-Only

The repo ships as a Claude Code plugin marketplace. Skills live in `skills/`, and the manifests live in `.claude-plugin/`.

## No Placeholder Slop

Avoid unresolved placeholders like `<your value here>` in skill examples. Use realistic dummy values such as `acme/webapp#812`, `https://example.com/dash`, or `lookback=20`.

## Env Vars For Secrets

Examples can name environment variables such as `TELEGRAM_BOT_TOKEN` or `GEMINI_API_KEY`, but they must never include real values.

## Keep The Edge Private

Public skills teach reusable technique. They do not ship private org lists, private paths, real client names, or production-tuned parameters.
