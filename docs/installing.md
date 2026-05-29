# Installing

Add the marketplace in Claude Code:

```text
/plugin marketplace add barobaonguyen/ai-automation-skills
```

Install the plugin:

```text
/plugin install ai-automation-skills@barobaonguyen
```

Confirm it appears:

```text
/plugin list
```

Skills should appear under the `ai-automation-skills:<skill>` namespace. If the marketplace command fails, update Claude Code first and retry from a clean session.

## Local Validation

From the repo root:

```bash
python scripts/validate_skills.py
claude plugin validate .
```

The Python validator is the CI gate. `claude plugin validate .` is the official local plugin check when the Claude CLI is installed.
