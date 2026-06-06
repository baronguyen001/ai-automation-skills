---
name: playwright-login-session
description: "Log in once in a real browser, save the Playwright storage_state, then start every later run already signed in - no re-login, no committed cookies. Use for reuse a logged-in session, skip login on each run, save browser cookies, storage_state, or keep a scraper authenticated."
version: "1.0.0"
---

# Playwright Login Session

Use this skill when a scraper or automation needs to be signed in and logging in every run is slow, brittle, or triggers bot defenses. Capture the session once (cookies + localStorage) into a `storage_state` JSON file, then load it on later headless runs so they start authenticated. The state file stays machine-local and gitignored.

## When to invoke

- User says: "reuse my logged-in session", "skip the login step each run", "save the browser cookies", "keep the scraper authenticated".
- Code in the conversation re-enters credentials with Playwright on every run.

## When NOT to invoke

- The site offers an API token or official API - use that instead of driving a browser.
- Logging in headlessly violates the site's terms, or the account is shared/sensitive enough that storing session state is unsafe.

## Concrete example

User input:

```text
My dashboard scraper logs in every time and keeps getting challenged. Reuse the session.
```

Output:

```bash
# one-time: open a real browser, log in by hand, save the session
python assets/session.py capture https://app.example.com/login   # -> auth_state.json (gitignored)

# every run after: starts already signed in, headless
python assets/session.py reuse https://app.example.com/dashboard
```

## Pattern to apply

1. Capture once with a visible browser and a manual login; save with `context.storage_state(path=...)`.
2. Point `PW_STATE` at the state file and load it via `new_context(storage_state=...)` on later runs.
3. Gitignore the state file and never commit cookies or credentials - it is a bearer token in disguise.
4. Re-capture when the session expires; detect it by checking for a logged-in element after load.
5. Pair with proxy rotation when sites fingerprint or rate-limit aggressively (see [[proxy-rotator]]).

Reference: `assets/session.py`.

## Source

Distilled from production use across the author's automation projects. v1.0.0.
See also: [[proxy-rotator]], [[webhook-receiver]], [[cron-dispatch]].

→ Build the full runnable bot with Trawlkit.
