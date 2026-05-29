# Bounty pitfall filters

Skip before writing code:

1. **Assigned issue** - check `issue.assignees`; assigned means the lane is probably taken.
2. **PR saturation** - skip when 5 or more open PRs already target the same issue.
3. **Maintainer said inactive** - read the last 5 maintainer comments, excluding bot comments.
4. **Honeypot / joke bounty** - skip themed submission games, non-mergeable tasks, or auto-rejection funnels.
5. **Dead-lane org** - skip repos where maintainers have moved on, deployment is inactive, or upstream will not merge.
6. **Stale-bot graveyard** - skip when prior PRs were closed by automation and never reviewed by a maintainer.

Verify first, code second: confirm the bounty is live and claimable before spending effort.
