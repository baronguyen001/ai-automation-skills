---
name: env-config-loader
description: "Load a .env file, validate that required keys are present, and read typed values (int/bool/float/list) with clear error messages - stdlib only, no python-dotenv, no pydantic. Use when the user asks to load a .env, validate config, fail fast on missing env vars, read an env var as an int or bool, or parse a comma-separated env list."
version: "1.0.0"
---

# Env Config Loader

Use this skill when a script reads configuration from the environment and you want it to fail fast at startup with a clear message - "missing required keys: API_BASE, RUN_LIMIT" - instead of a `KeyError` halfway through, or a silent string-vs-int bug. It parses a simple `.env`, overlays the real environment, checks a required-key list once, and exposes typed getters (`get_int`, `get_bool`, `get_float`, `get_list`) that raise readable errors on bad values. No `python-dotenv`, no `pydantic`.

## When to invoke

- User says: "load my .env", "validate config at startup", "fail fast if an env var is missing", "read this env var as an int / bool / list".
- Code in the conversation calls `os.environ[...]` scattered around with no central validation.

## When NOT to invoke

- A large nested config with deep schemas and cross-field rules - reach for `pydantic-settings`.
- Secrets live in a vault/secret manager, not env/.env; load from there instead.

## Concrete example

User input:

```text
Read API_BASE, RUN_LIMIT (int), and DRY_RUN (bool) from .env, and crash early with a clear message if any are missing.
```

Output:

```python
# Copy assets/config.py into your project, then:
from config import Config

cfg = Config.load(".env", required=["API_BASE", "RUN_LIMIT"])

base = cfg.get("API_BASE")                       # str, guaranteed present
limit = cfg.get_int("RUN_LIMIT")                 # ValueError if not an int
dry_run = cfg.get_bool("DRY_RUN", default=False) # true/1/yes/on -> True
tags = cfg.get_list("TAGS", default=[])          # "a,b,c" -> ["a", "b", "c"]
```

If `API_BASE` or `RUN_LIMIT` is absent, `Config.load` raises `ConfigError: missing required keys: ...` at startup, before any work begins. `.env` ships as `.env.example` with placeholders only - never real values.

## Pattern to apply

1. Parse `.env` permissively: skip blanks/`#` comments, support `export KEY=val` and quoted values.
2. Let the real process environment win over `.env`, so production overrides the file.
3. Validate the `required` list once in `load()` and raise a single error listing every missing key.
4. Use typed getters; coerce explicitly and raise a clear `ConfigError` on a bad value, never a silent default.
5. Commit only `.env.example` with obvious placeholders; keep the real `.env` gitignored.

Reference: `assets/config.py`.

## Source

Distilled from production use across the author's automation projects. v1.0.0.
See also: [[config-audit-checklist]], [[telegram-alerter]], [[slack-webhook-alerter]].

→ Build the full runnable bot with Trawlkit.
