---
name: gemini-structured-output
description: "Get validated JSON out of Gemini using a Pydantic model - convert the model to responseSchema, set responseMimeType, then parse and validate the response, with a salvage parser for JSON wrapped in prose. Use for gemini structured output, gemini json schema, pydantic to gemini, or responseSchema."
---

# Gemini Structured Output

Use this skill when Gemini should return validated JSON instead of prose. It covers the modern `google-genai` SDK path and a salvage parser for older REST-style responses.

## When to invoke

- User says: "gemini structured output" / "gemini json schema" / "pydantic to gemini" / "responseSchema"
- Code in the conversation uses: Pydantic models, JSON validation, or Gemini response schemas.

## When NOT to invoke

- The user needs streaming structured output.
- The schema requires deep unions, recursive references, or complex OpenAPI features.

## Concrete example

User input:

```text
Make Gemini return a validated verdict object for this idea score.
```

Output:

```python
from pydantic import BaseModel
from google import genai


class Verdict(BaseModel):
    label: str
    score: int
    reasons: list[str]


client = genai.Client()
resp = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Score this idea 0-100 and label GO/NO-GO: a CLI that lints SKILL.md files.",
    config={"response_mime_type": "application/json", "response_schema": Verdict},
)
verdict = Verdict.model_validate_json(resp.text)
print(verdict.label, verdict.score)
```

For REST or older SDK paths, use `extract_json()` from the asset before Pydantic validation.

## Pattern to apply

1. Define the expected output as a Pydantic model.
2. Pass the model as `response_schema` and set `response_mime_type` to `application/json`.
3. Validate `resp.text` back into the model.
4. If the model wraps JSON in markdown/prose, depth-match the first balanced JSON object and validate that.
5. If Gemini rejects the schema, flatten nested models and avoid `$ref`, deep `oneOf`, and deep `anyOf`.

Reference: `assets/structured.py`.

## Source

Distilled from production use across the author's automation projects. v0.1.0.
See also: [[gemini-cost-tracker]].
