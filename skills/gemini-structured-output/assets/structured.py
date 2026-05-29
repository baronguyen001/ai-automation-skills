import json
import re
from typing import Any

from google import genai
from pydantic import BaseModel


class Verdict(BaseModel):
    label: str
    score: int
    reasons: list[str]


def call_gemini_for_verdict(prompt: str, model: str = "gemini-2.5-flash") -> Verdict:
    client = genai.Client()
    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": Verdict,
        },
    )
    return Verdict.model_validate_json(response.text)


def extract_json(text: str) -> dict[str, Any]:
    cleaned = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE)
    cleaned = cleaned.strip()

    try:
        parsed = json.loads(cleaned)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass

    start = cleaned.find("{")
    if start < 0:
        raise ValueError("no JSON object found")

    depth = 0
    in_string = False
    escaped = False

    for index in range(start, len(cleaned)):
        char = cleaned[index]
        if escaped:
            escaped = False
            continue
        if char == "\\" and in_string:
            escaped = True
            continue
        if char == '"':
            in_string = not in_string
            continue
        if in_string:
            continue

        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                parsed = json.loads(cleaned[start : index + 1])
                if isinstance(parsed, dict):
                    return parsed

    raise ValueError("no balanced JSON object found")
