---
name: cron-dispatch
description: "Schedule any script to run on a recurring schedule on Windows (Task Scheduler) or Linux (cron) - register, list, and remove jobs from one command, with logging to a file and a guard against overlapping runs. Use for schedule a script, run nightly, set up a cron job, windows task scheduler, or run on a timer."
version: "1.0.0"
---

# Cron Dispatch

Use this skill when a script must run unattended on a schedule and the same pattern has to work on both a Windows dev box and a Linux server. It gives copy-paste setup for Windows Task Scheduler and Linux cron, plus logging and an overlap guard so a slow run never stacks on top of the next tick.

## When to invoke

- User says: "run this nightly" / "set up a cron job" / "schedule a script" / "windows task scheduler"
- Code in the conversation uses: a standalone script (Python, Node, shell) that should fire on a timer instead of by hand.

## When NOT to invoke

- The work belongs inside an existing always-on service or event loop, not an OS scheduler.
- The user wants a managed cloud scheduler (GitHub Actions cron, cloud functions) rather than a local machine.

## Concrete example

User input:

```text
Run my scraper.py every day at 9am on Windows now, and give me the Linux cron line for the server later.
```

Output:

```powershell
# Windows: register a daily 09:00 task (run from the repo root)
powershell -ExecutionPolicy Bypass -File assets/setup_task.ps1 `
  -TaskName "scraper-daily" `
  -Command "python" `
  -Arguments "E:\proj\scraper.py" `
  -Time "09:00"
```

```bash
# Linux: same job, 09:00 daily, logged, no overlap
0 9 * * * cd /srv/proj && flock -n /tmp/scraper.lock python scraper.py >> /srv/proj/cron.log 2>&1
```

## Pattern to apply

1. Pick one schedule expression and translate it to both Task Scheduler triggers and a 5-field cron line.
2. Always run the script from its project directory so relative paths resolve.
3. Append stdout and stderr to a log file; never rely on a console that no one is watching.
4. Guard against overlap (`flock` on Linux, `-MultipleInstances IgnoreNew` on Windows) so a long run does not double up.
5. Register, list, and remove by a stable task name so re-running setup stays idempotent.

Reference: `assets/setup_task.ps1`, `assets/cron_linux.sh`.

## Source

Distilled from production use across the author's automation projects. v1.0.0.
See also: [[pipeline-orchestrator]], [[telegram-alerter]].

→ Build the full runnable bot with Trawlkit.
