# Pre-backtest / pre-deploy config audit

- [ ] A single config-snapshot doc exists and is named, such as `PRODUCTION_CONFIG.md`.
- [ ] Snapshot `Last verified` date is less than 30 days old.
- [ ] Every value in the snapshot matches `.env`; list mismatches explicitly.
- [ ] README default values match the snapshot, or README clearly says defaults are not live settings.
- [ ] `Common mistakes` section lists gotchas the validation job must replicate, such as scored-but-not-hard-gated checks or filters that legitimately zero out some periods.
- [ ] Validation baseline params are copied from the snapshot, not from README prose.
