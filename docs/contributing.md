# Contributing

This repo keeps skills small, concrete, and installable.

## Add A Skill

1. Create `skills/<skill-name>/SKILL.md`.
2. Use kebab-case for the folder and `name`.
3. Keep frontmatter to documented fields only: `name`, `description`, and optional Claude skill fields such as `argument-hint` or `allowed-tools`.
4. Add a real `## Concrete example` with realistic dummy values.
5. Put reusable code or templates under the skill's `assets/`, `prompts/`, or `examples/` folder.

## Validate

Run:

```bash
python scripts/validate_skills.py
claude plugin validate .
```

The Python validator checks JSON manifests, skill frontmatter, concrete examples, Python asset syntax, and common secret patterns. The Claude CLI check validates the plugin structure when available locally.

## Sanitization Rules

- Do not commit `.env` or any credential.
- Use environment variable names in examples, never real values.
- Do not ship hidden org lists, private client names, personal handles, or production-tuned parameters.
- Genericize examples so the useful pattern remains without exposing private workflow details.
