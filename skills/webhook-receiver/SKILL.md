---
name: webhook-receiver
description: "Receive inbound webhooks with no web framework - a tiny stdlib HTTP server that verifies an HMAC signature in constant time and queues each payload to disk for a worker to process. Use for receive a webhook, handle an incoming POST, trigger a script from a webhook, verify a webhook signature, or stripe/github/telegram webhook intake."
version: "1.0.0"
---

# Webhook Receiver

Use this skill when an external service must trigger your script by POSTing to a URL, and you want to authenticate and durably capture deliveries without pulling in Flask/FastAPI. It is an `http.server` receiver that rejects unsigned requests and writes each verified payload to a queue directory, so a slow downstream job never blocks or drops an event.

## When to invoke

- User says: "receive a webhook", "handle an incoming POST", "trigger my script when X happens", "verify the webhook signature".
- Code in the conversation needs to ingest events from Stripe/GitHub/Telegram/a SaaS without a heavy web stack.

## When NOT to invoke

- The project already runs a web framework (Flask/FastAPI/Django) - add a route there instead.
- The provider supports polling and you do not control a public URL; use a scheduled pull (see [[cron-dispatch]]).

## Concrete example

User input:

```text
Stripe needs to POST events to my box and run reconcile.py. Authenticate it and don't lose events.
```

Output:

```bash
export WEBHOOK_SECRET="whsec_..."         # shared secret from the provider
export WEBHOOK_QUEUE="events"             # one JSON file per delivery
python assets/receiver.py                 # listens on :8080, 401s bad signatures

# reconcile.py drains ./events on a timer (see cron-dispatch) - decoupled from intake
```

## Pattern to apply

1. Read the shared secret only from the environment; never hardcode it.
2. Compute HMAC-SHA256 over the raw body and compare in constant time (`hmac.compare_digest`) - reject mismatches with 401.
3. Cap the body size and require valid JSON before accepting, so a bad caller cannot exhaust memory.
4. Persist the payload to a queue directory and return 202 immediately; let a separate worker process it.
5. Keep intake and processing decoupled so a slow or crashed worker never drops a delivery.

Reference: `assets/receiver.py`.

## Source

Distilled from production use across the author's automation projects. v1.0.0.
See also: [[sqlite-state]], [[cron-dispatch]], [[pipeline-orchestrator]].

→ Build the full runnable bot with Trawlkit.
